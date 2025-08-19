import pytest
from decimal import Decimal
from orders.models import Order, OrderItem
from users.models import User
from products.models import Products, Categories, Brands


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
    product = Products.objects.create(name='Product 1', brand=brand, category=category, price=Decimal('1000.00'),
                                      slug='product-1')
    product.sell_price = lambda: '1000'
    return product


@pytest.fixture
def product_with_spaces(db):
    category = Categories.objects.create(name='Смартфоны', slug='smartphones')
    brand = Brands.objects.create(name='Test brand', slug='test-brand')
    product = Products.objects.create(name='Product 2', brand=brand, category=category, price=Decimal('1000.00'),
                                      slug='product-2')
    product.sell_price = lambda: '1 000'
    return product


@pytest.fixture
def order(db, user):
    return Order.objects.create(user=user, phone_number='1234567890')


@pytest.fixture
def empty_order(db):
    return Order.objects.create(phone_number='1234567890')


def test_products_price_without_spaces(order, product):
    order_item = OrderItem.objects.create(
        order=order, product=product, name='Товар 1',
        price=Decimal('1000.00'), quantity=2
    )
    assert order_item.products_price() == 2000


def test_products_price_with_spaces(order, product_with_spaces):
    order_item = OrderItem.objects.create(
        order=order, product=product_with_spaces, name='Товар 2', price=Decimal('1000.00'), quantity=3
    )
    assert order_item.products_price() == 3000


@pytest.mark.django_db
def test_total_price_and_quantity(order, product):
    OrderItem.objects.create(order=order, product=product, name='A', price=Decimal('500.00'), quantity=5)
    OrderItem.objects.create(order=order, product=product, name='B', price=Decimal('500.00'), quantity=1)

    items = OrderItem.objects.all()
    assert items.total_price() == 3000
    assert items.total_quantity() == 6


@pytest.mark.django_db
def test_total_quantity_empty_queryset():
    assert OrderItem.objects.all().total_quantity() == 0


@pytest.mark.django_db
def test_order_str(order):
    assert str(order) == f'Заказ № {order.pk} | Покупатель Иван Иванов'


@pytest.mark.django_db
def test_order_item_str(order, product):
    order_item = OrderItem.objects.create(
        order=order, product=product, name='Товар X',
        price=Decimal("1000.00"), quantity=1
    )
    assert str(order_item) == f"Товар Товар X | Заказ № {order.pk}"


@pytest.mark.django_db
def test_order_with_delivery_and_payment_flags(user):
    order = Order.objects.create(
        user=user,
        phone_number='79999999999',
        requires_delivery=True,
        delivery_address='г. Москва, ул. Ленина, д. 5',
        payment_on_get=True,
        is_paid=False,
        status="В пути"
    )

    assert order.requires_delivery is True
    assert order.delivery_address == 'г. Москва, ул. Ленина, д. 5'
    assert order.payment_on_get is True
    assert order.is_paid is False
    assert order.status == 'В пути'
    assert str(order) == f"Заказ № {order.pk} | Покупатель Иван Иванов"


def test_order_defaults_without_user(empty_order):
    assert empty_order.user is None
    assert empty_order.requires_delivery is False
    assert empty_order.delivery_address is None
    assert empty_order.payment_on_get is False
    assert empty_order.is_paid is False
    assert empty_order.status == "В обработке"
