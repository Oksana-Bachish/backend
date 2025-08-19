import pytest
from django.urls import reverse
from django.test import RequestFactory, Client
from decimal import Decimal
from django.contrib.sessions.middleware import SessionMiddleware
from unittest.mock import patch, MagicMock
from orders.models import Order, OrderItem
from users.models import User
from products.models import Products, Categories, Brands
from payment.views import PaymentProcessView, PaymentCompletedView, PaymentCanceledView


def add_session_to_request(request):
    """Добавляет middleware сессии вручную"""
    middleware = SessionMiddleware(get_response=lambda r: None)
    middleware.process_request(request)
    request.session.save()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username='testuser',
        password='12345',
        first_name='Иван',
        last_name='Иванов'
    )


@pytest.fixture
def product(db):
    category = Categories.objects.create(name='Смартфоны', slug='smartphones')
    brand = Brands.objects.create(name='Test brand', slug='test-brand')
    return Products.objects.create(name='Test product', brand=brand, category=category, slug='test_product')


@pytest.fixture
def order(db, user):
    return Order.objects.create(user=user, phone_number='1234567890', requires_delivery='0', delivery_address='',
                                payment_on_get='0')


@pytest.fixture
def order_items(db, order, product):
    item1 = OrderItem.objects.create(order=order, product=product, price=Decimal('10000.00'), quantity=2,
                                     name='Тестовый продукт 1')
    item2 = OrderItem.objects.create(order=order, product=product, price=Decimal('5000.00'), quantity=1,
                                     name='Тестовый продукт 2')
    return [item1, item2]


@pytest.mark.django_db
@patch('payment.views.stripe.checkout.Session.create')
def test_form_valid_creates_stripe_sessions(mock_stripe_session_create, order, order_items):
    mock_session = MagicMock()
    mock_session.url = 'http://fake-stripe-checkout-url'
    mock_stripe_session_create.return_value = mock_session

    factory = RequestFactory()
    request = factory.post(reverse('payment:process'))
    add_session_to_request(request)
    request.session['order_id'] = order.id

    response = PaymentProcessView.as_view()(request)

    # Проверяем, что Stripe Session.create вызвался с правильными параметрами
    args, kwargs = mock_stripe_session_create.call_args
    assert kwargs['mode'] == 'payment'
    assert kwargs['client_reference_id'] == order.id
    assert 'line_items' in kwargs
    # Проверяем, что response — редирект на session.url
    assert response.status_code == 302
    assert response.url == mock_session.url


@pytest.mark.django_db
def test_get_order_and_items_returns_order_and_items(order, order_items):
    factory = RequestFactory()
    request = factory.get('/')
    add_session_to_request(request)
    request.session['order_id'] = order.id

    view = PaymentProcessView()
    view.request = request

    order_result, items_result = view.get_order_and_items()

    assert order_result == order
    assert list(items_result) == order_items


@pytest.mark.django_db
def test_get_context_data_includes_order_and_items(order, order_items):
    factory = RequestFactory()
    request = factory.get('/')
    add_session_to_request(request)
    request.session['order_id'] = order.id

    view = PaymentProcessView()
    view.request = request

    context = view.get_context_data()

    assert context['order'] == order
    assert list(context['order_items']) == order_items


@pytest.mark.django_db
def test_payment_completed_view_context_and_template():
    client = Client()
    url = reverse('payment:completed')
    response = client.get(url)

    assert response.status_code == 200
    assert 'payment/completed.html' in (t.name for t in response.templates)
    assert response.context_data['title'] == 'Оплата прошла успешно'


@pytest.mark.django_db
def test_payment_canceled_view_context_and_template():
    client = Client()
    url = reverse('payment:canceled')
    response = client.get(url)

    assert response.status_code == 200
    assert 'payment/canceled.html' in (t.name for t in response.templates)
    assert response.context_data['title'] == 'Платеж отменен'
