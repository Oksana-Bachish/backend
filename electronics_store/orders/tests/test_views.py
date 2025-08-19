import pytest
from decimal import Decimal
from django.urls import reverse
from django.contrib.messages import get_messages
from django.core.exceptions import ValidationError
from baskets.models import Basket
from orders.models import Order, OrderItem
from products.models import Products, Categories, Brands
from users.models import User


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
    return Products.objects.create(name='Test product', brand=brand, category=category, price=Decimal('1000.00'),
                                   quantity=3, slug='test_product')


@pytest.fixture
def basket(user, product):
    return Basket.objects.create(user=user, product=product, quantity=2)


@pytest.mark.django_db
def test_get_initial_fill(client, user):
    client.force_login(user)
    url = reverse('orders:create_order')
    response = client.get(url)
    assert response.status_code == 200
    assert 'value="Иван' in response.content.decode()
    assert 'value="Иванов' in response.content.decode()


@pytest.mark.django_db
def test_post_create_order_payment_0(client, user, product, basket):
    client.force_login(user)
    url = reverse('orders:create_order')
    data = {
        'first_name': 'Иван',
        'last_name': 'Иванов',
        'phone_number': '1234567890',
        'requires_delivery': '0',
        'delivery_address': '',
        'payment_on_get': '0',  # оплата НЕ при получении, значит редирект на оплату
    }

    response = client.post(url, data)

    # Проверяем, что заказ создан
    order = Order.objects.filter(user=user).first()
    assert order is not None
    assert order.phone_number == '1234567890'

    # Проверяем, что корзина очищена
    assert Basket.objects.filter(user=user).count() == 0

    # Проверяем редирект на оплату
    assert response.status_code == 302
    assert response.url == reverse('payment:process')

    # Проверяем, что в сессии есть order_id
    session = client.session
    assert session['order_id'] == order.id


@pytest.mark.django_db
def test_post_create_order_payment_1(client, user, product, basket):
    client.force_login(user)
    url = reverse('orders:create_order')
    data = {
        'first_name': 'Иван',
        'last_name': 'Иванов',
        'phone_number': '1234567890',
        'requires_delivery': '1',
        'delivery_address': 'Москва, ул. Пушкина',
        'payment_on_get': '1',  # оплата при получении, значит редирект на профиль
    }
    response = client.post(url, data, follow=True)

    # Проверяем, что заказ создан
    order = Order.objects.filter(user=user).first()
    assert order is not None

    # Проверяем, что корзина очищена
    assert Basket.objects.filter(user=user).count() == 0

    # Проверяем редирект на профиль
    assert response.redirect_chain[-1][0] == reverse('users:profile')

    # Проверяем, что есть success сообщение
    messages = list(get_messages(response.wsgi_request))
    assert any('Заказ оформлен' in str(m) for m in messages)


@pytest.mark.django_db
def test_post_create_order_not_enough_quantity(client, user, product):
    client.force_login(user)
    Basket.objects.create(user=user, product=product, quantity=5)  # Запрос больше, чем есть

    url = reverse('orders:create_order')
    data = {
        'first_name': 'Иван',
        'last_name': 'Иванов',
        'phone_number': '1234567890',
        'requires_delivery': '0',
        'delivery_address': '',
        'payment_on_get': '1',
    }
    response = client.post(url, data, follow=True)

    # Проверяем, что заказ НЕ создан
    assert not Order.objects.filter(user=user).exists()

    # Проверяем, что корзина НЕ очищена
    assert Basket.objects.filter(user=user).exists()

    # Проверяем, что есть сообщение об ошибке
    messages = list(get_messages(response.wsgi_request))
    assert any('Недостаточное количество товара' in str(m) for m in messages)


@pytest.mark.django_db
def test_post_create_order_invalid_form(client, user):
    client.force_login(user)
    url = reverse('orders:create_order')
    data = {
        'first_name': '',
        'last_name': '',
        'phone_number': 'not_a_number',
        'requires_delivery': '0',
        'delivery_address': '',
        'payment_on_get': '0',
    }

    response = client.post(url, data, follow=True)

    # Проверяем, что заказ НЕ создан
    assert not Order.objects.filter(user=user).exists()

    # Проверяем, что есть ошибка с заполнением
    messages = list(get_messages(response.wsgi_request))
    assert any('Заполните все обязательные поля' in str(m) for m in messages)
