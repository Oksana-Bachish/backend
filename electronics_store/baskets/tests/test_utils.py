import pytest
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory
from baskets.models import Basket
from baskets.utils import get_user_baskets
from users.models import User
from products.models import Products, Brands, Categories
from django.contrib.auth.models import AnonymousUser


@pytest.fixture
def product(db):
    brand = Brands.objects.create(name='Test brand', slug='test-brand')
    category = Categories.objects.create(name='Смартфоны', slug='smartphones')
    return Products.objects.create(name='Test product', slug='test-product', price=35000.00, brand=brand,
                                   category=category)


@pytest.fixture
def rf():
    return RequestFactory()


def add_session_to_request(request):
    """Добавляет middleware сессии вручную"""
    middleware = SessionMiddleware(get_response=lambda r: None)
    middleware.process_request(request)
    request.session.save()


@pytest.mark.django_db
def test_get_user_baskets_authentificated(rf, product):
    user = User.objects.create_user(username='user', password='1234')
    basket = Basket.objects.create(user=user, product=product, quantity=4)

    request = rf.get('/')
    request.user = user

    baskets = get_user_baskets(request)
    assert list(baskets) == [basket]


@pytest.mark.django_db
def test_get_user_baskets_anonymous_with_session(rf, product):
    request = rf.get('/')
    request.user = AnonymousUser()

    add_session_to_request(request)
    basket = Basket.objects.create(product=product, quantity=5, session_key=request.session.session_key)
    baskets = get_user_baskets(request)
    assert list(baskets) == [basket]


@pytest.mark.django_db
def test_get_user_baskets_anonymous_without_session(rf, product):
    request = rf.get('/')
    request.user = AnonymousUser()

    add_session_to_request(request)

    baskets = get_user_baskets(request)
    assert list(baskets) == []
