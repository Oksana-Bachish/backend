import pytest
from products.models import Categories, Brands, Products, Characteristics, ProductImage


@pytest.mark.django_db
def test_create_category():
    category = Categories.objects.create(name='Смартфоны', slug='smartphones')
    assert category.name == 'Смартфоны'
    assert category.slug == 'smartphones'
    assert str(category) == 'Смартфоны'


@pytest.mark.django_db
def test_create_brand():
    brand = Brands.objects.create(name='Apple', slug='apple')
    assert brand.name == 'Apple'
    assert brand.slug == 'apple'
    assert str(brand) == 'Apple'


@pytest.mark.django_db
def test_create_product_with_foreign_keys():
    category = Categories.objects.create(name='Смартфоны', slug='smartphones')
    brand = Brands.objects.create(name='Samsung', slug='samsung')
    product = Products.objects.create(name='Samsung Galaxy S25 Ultra',
                                      slug='samsung-galaxy-s25-ultra',
                                      price=140000.00,
                                      discount=10.00,
                                      quantity=10,
                                      brand=brand,
                                      category=category)
    assert product.name == 'Samsung Galaxy S25 Ultra'
    assert product.brand == brand
    assert product.category == category
    assert product.sell_price() == '126 000'


@pytest.mark.django_db
def test_characteristics_linked_to_product():
    category = Categories.objects.create(name='Смартфоны', slug='smartphones')
    brand = Brands.objects.create(name='Xiaomi', slug='xiaomi')
    product = Products.objects.create(
        name='Xiaomi Redmi Note 14 Pro+',
        slug='xiaomi-redmi-note-14-pro',
        price=55000.00,
        brand=brand,
        category=category
    )
    characteristics = Characteristics.objects.create(
        product=product,
        operating_system='Android',
        processor='Snapdragon 7s Gen 3',
        screen_diagonal=6.67,
        built_in_memory=512,
        random_access_memory=12,
    )
    assert characteristics.product == product
    assert characteristics.operating_system == 'Android'
