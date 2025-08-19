import pytest
from decimal import Decimal
from django.contrib.admin.sites import AdminSite
from baskets.admin import BasketAdmin
from baskets.models import Basket
from users.models import User
from products.models import Products, Categories, Brands


@pytest.fixture
def admin_site():
    return AdminSite()


@pytest.fixture
def basket_admin(admin_site):
    return BasketAdmin(Basket, admin_site)


@pytest.fixture
def product(db):
    category = Categories.objects.create(name='Смартфоны', slug='smartphones')
    brand = Brands.objects.create(name='Test brand', slug='test-brand')
    return Products.objects.create(name='Test product', brand=brand, category=category, price=Decimal('1000.00'),
                                   quantity=3, slug='test_product')


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username='testuser',
        password='12345',
        first_name='Иван',
        last_name='Иванов'
    )


@pytest.fixture
def basket(db, user, product):
    return Basket.objects.create(user=user, product=product, quantity=3)


@pytest.fixture
def anon_basket(db, product):
    return Basket.objects.create(user=None, product=product, quantity=1)


def test_user_display(basket_admin, basket, user):
    assert basket_admin.user_display(basket) == str(user)


def test_user_display_anonymous(basket_admin, anon_basket):
    assert basket_admin.user_display(anon_basket) == 'Анонимный пользователь'


def test_product_display(basket_admin, basket, product):
    assert basket_admin.product_display(basket) == product.name


def test_list_display(basket_admin):
    assert basket_admin.list_display == ['user_display', 'product_display', 'quantity', 'created_timestamp']


def test_list_filter(basket_admin):
    assert basket_admin.list_filter == ['created_timestamp', 'user', 'product__name']

