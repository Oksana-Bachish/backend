import pytest
from baskets.models import Basket
from products.models import Products, Brands, Categories
from users.models import User


@pytest.mark.django_db
def test_basket_str_authenticated_user():
    user = User.objects.create_user(username='user1', password='1234')

    brand = Brands.objects.create(name='Test brand', slug='test-brand')
    category = Categories.objects.create(name='Смартфоны', slug='smartphones')
    product = Products.objects.create(name='Test prod', slug='test-prod', price=20000.00, brand=brand,
                                      category=category)

    basket = Basket.objects.create(user=user, product=product, quantity=3)

    expected_str = f'Корзина {user.username} | Товар {product.name} | Количество {basket.quantity}'
    assert str(basket) == expected_str


@pytest.mark.django_db
def test_basket_str_anonymus():
    brand = Brands.objects.create(name='Test brand', slug='test-brand')
    category = Categories.objects.create(name='Смартфоны', slug='smartphones')
    product = Products.objects.create(name='Test product', slug='test-product', price=35000.00, brand=brand, category=category)

    basket = Basket.objects.create(product=product, quantity=4)

    expected_price = 35000.00 * 4
    assert basket.product_price() == expected_price


@pytest.mark.django_db
def test_basket_queryset_total_quantity_price():
    brand = Brands.objects.create(name='Test brand', slug='test-brand')
    category = Categories.objects.create(name='Планшеты', slug='tablets')
    product = Products.objects.create(name='Test product', slug='test-product', price=50000.00, brand=brand, category=category)

    basket1 = Basket.objects.create(quantity=2, product=product)
    basket2 = Basket.objects.create(quantity=3, product=product)
    baskets = Basket.objects.all()
    assert baskets.total_quantity() == 5
    assert baskets.total_price() == basket1.product_price() + basket2.product_price()
