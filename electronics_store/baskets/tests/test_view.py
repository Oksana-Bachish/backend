import pytest
import json
from django.urls import reverse
from baskets.models import Basket
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory
from baskets.views import BasketAddView, BasketChangeView, BasketRemoveView
from products.models import Products, Brands, Categories
from users.models import User


@pytest.fixture
def product(db):
    brand = Brands.objects.create(name='Test brand', slug='test-brand')
    category = Categories.objects.create(name='Смартфоны', slug='smartphones')
    return Products.objects.create(name='Test product', slug='test-product', price=35000.00, brand=brand,
                                   category=category)


@pytest.fixture
def user(db):
    return User.objects.create_user(username='user1', password='1234')


@pytest.fixture
def rf():
    return RequestFactory()


def add_session_to_request(request):
    """Добавляет middleware сессии вручную"""
    middleware = SessionMiddleware(get_response=lambda r: None)
    middleware.process_request(request)
    request.session.save()


@pytest.mark.django_db
def test_basket_add_view_authenticated_user(rf, user, product):
    url = reverse('basket:basket_add')
    request = rf.post(url, {'product_id': product.id})
    request.user = user

    add_session_to_request(request)

    response = BasketAddView.as_view()(request)

    assert response.status_code == 200
    data = json.loads(response.content)
    assert data['message'] == 'Товар добавлен в корзину'
    assert Basket.objects.filter(user=user, product=product).exists()


@pytest.mark.django_db
def test_basket_add_view_anonymous_user(rf, product):
    url = reverse('basket:basket_add')
    request = rf.post(url, {'product_id': product.id})
    request.user = AnonymousUser()

    add_session_to_request(request)

    response = BasketAddView.as_view()(request)

    assert response.status_code == 200
    data = json.loads(response.content)
    assert data['message'] == 'Товар добавлен в корзину'
    assert Basket.objects.filter(session_key=request.session.session_key, product=product).exists()


@pytest.mark.django_db
def test_basket_change_view_authenticated_user(rf, user, product):
    basket = Basket.objects.create(user=user, product=product, quantity=1)
    new_quantity = 5

    url = reverse('basket:basket_change')
    request = rf.post(url, {'basket_id': basket.id, 'quantity': new_quantity})
    request.user = user

    add_session_to_request(request)

    response = BasketChangeView.as_view()(request)

    assert response.status_code == 200
    data = json.loads(response.content)
    basket.refresh_from_db()
    assert basket.quantity == new_quantity
    assert data['message'] == 'Количество изменено'
    assert str(new_quantity) in data['basket_items_html']


@pytest.mark.django_db
def test_basket_change_view_anonymous_user(rf, product):
    request = rf.post(reverse('basket:basket_change'))
    request.user = AnonymousUser()

    add_session_to_request(request)

    # Создаём корзину с привязкой к сессии
    basket = Basket.objects.create(
        session_key=request.session.session_key,
        product=product,
        quantity=2
    )
    new_quantity = 3

    request.POST = request.POST.copy()
    request.POST['basket_id'] = basket.id
    request.POST['quantity'] = new_quantity

    response = BasketChangeView.as_view()(request)

    assert response.status_code == 200
    data = json.loads(response.content)
    basket.refresh_from_db()
    assert basket.quantity == new_quantity
    assert data['message'] == 'Количество изменено'


@pytest.mark.django_db
def test_basket_remove_view_authenticated_user(rf, user, product):
    basket = Basket.objects.create(user=user, product=product, quantity=4)

    url = reverse('basket:basket_remove')
    request = rf.post(url, {'basket_id': basket.id})
    request.user = user

    add_session_to_request(request)

    response = BasketRemoveView.as_view()(request)

    assert response.status_code == 200
    data = json.loads(response.content)
    assert data['message'] == 'Товар удален из корзины'
    assert data['quantity_deleted'] == 4
    assert not Basket.objects.filter(id=basket.id).exists()


@pytest.mark.django_db
def test_basket_remove_view_anonymous_user(rf, product):
    request = rf.post(reverse('basket:basket_remove'))
    request.user = AnonymousUser()

    add_session_to_request(request)

    basket = Basket.objects.create(
        session_key=request.session.session_key,
        product=product,
        quantity=2
    )

    request.POST = request.POST.copy()
    request.POST['basket_id'] = basket.id

    response = BasketRemoveView.as_view()(request)

    assert response.status_code == 200
    data = json.loads(response.content)
    assert data['message'] == 'Товар удален из корзины'
    assert data['quantity_deleted'] == 2
    assert not Basket.objects.filter(id=basket.id).exists()

