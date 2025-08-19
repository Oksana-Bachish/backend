import pytest
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from django.urls import reverse
from django.contrib.sessions.middleware import SessionMiddleware
from baskets.models import Basket
from baskets.mixins import BasketMixin
from baskets.utils import get_user_baskets
from products.models import Products, Brands, Categories
from users.models import User


@pytest.fixture
def rf():
    return RequestFactory()


@pytest.fixture
def product(db):
    brand = Brands.objects.create(name='Test brand', slug='test-brand')
    category = Categories.objects.create(name='Смартфоны', slug='smartphones')
    return Products.objects.create(name='Test prod', slug='test-prod', price=50000.00, brand=brand,
                                      category=category)


@pytest.fixture
def user(db):
    return User.objects.create_user(username='user', password='12345')


def add_session_to_request(request):
    middleware = SessionMiddleware(get_response=lambda r: None)
    middleware.process_request(request)
    request.session.save()


class DummyView(BasketMixin):
    pass


@pytest.mark.django_db
def test_get_basket_authenticated_user(rf, user, product):
    basket = Basket.objects.create(user=user, product=product, quantity=1)

    request = rf.get('/')
    request.user = user

    view = DummyView()
    result = view.get_basket(request, product=product)

    assert result == basket


@pytest.mark.django_db
def test_get_basket_anonymous_user_by_session_key(rf, product):
    request = rf.get('/')
    request.user = AnonymousUser()
    add_session_to_request(request)

    basket = Basket.objects.create(product=product, quantity=1, session_key=request.session.session_key)

    view = DummyView()
    result = view.get_basket(request, product=product)

    assert result == basket


@pytest.mark.django_db
def test_get_basket_by_id(rf, user, product):
    basket = Basket.objects.create(user=user, product=product, quantity=2)

    request = rf.get('/')
    request.user = user

    view = DummyView()
    result = view.get_basket(request, basket_id=basket.id)

    assert result == basket


@pytest.mark.django_db
def test_render_basket_adds_order_key_if_referer_matches(rf, user, product):
    basket = Basket.objects.create(user=user, product=product, quantity=2)

    request = rf.get('/')
    request.user = user
    referer_url = reverse('orders:create_order')
    request.META['HTTP_REFERER'] = referer_url

    view = DummyView()
    html = view.render_basket(request)

    # Проверим, что отрендерился HTML и фрагмент есть в нём
    assert 'Итого' in html
    assert str(basket.quantity) in html
    assert product.name in html
