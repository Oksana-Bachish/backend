import pytest
from django.urls import reverse
from products.models import Products, Categories, Brands, Characteristics
from products.views import CatalogView, ProductView

pytestmark = pytest.mark.django_db


@pytest.fixture
def sample_product():
    category = Categories.objects.create(name='Смартфоны', slug='smartphones')
    brand = Brands.objects.create(name='Huawei', slug='huawei')
    product = Products.objects.create(name='Huawei Mate X6',
                                      slug='huawei-mate-x6',
                                      price=135000.00,
                                      discount=3.00,
                                      quantity=10,
                                      brand=brand,
                                      category=category)
    Characteristics.objects.create(
        product=product,
        color='черный',
        built_in_memory=128,
        random_access_memory=6,
        main_camera=48,
    )
    product.refresh_from_db()
    return product


def test_catalog_view_status_code(client, sample_product):
    url = reverse('products:index', kwargs={'category_slug': 'smartphones'})
    response = client.get(url)
    assert response.status_code == 200
    assert b'Huawei Mate X6' in response.content


def test_catalog_view_on_sale_filter(client, sample_product):
    url = reverse('products:index', kwargs={'category_slug': 'smartphones'})
    response = client.get(url, {'on_sale': '1'})
    assert sample_product.discount > 0
    assert b'Huawei Mate X6' in response.content


def test_catalog_view_brand_filter(client, sample_product):
    url = reverse('products:index', kwargs={'category_slug': 'smartphones'})
    response = client.get(url, {'select_brand': 'Huawei'})
    assert response.status_code == 200
    assert b'Huawei Mate X6' in response.content


def test_filter_by_multiple_brands(client):
    brand1 = Brands.objects.create(name="Huawei")
    brand2 = Brands.objects.create(name="Samsung")
    category = Categories.objects.create(name="Смартфоны", slug="smartphones")

    product1 = Products.objects.create(name="Huawei Mate XT", brand=brand1, category=category, slug='huawei-mate-xt')
    product2 = Products.objects.create(name="Samsung Galaxy S24", brand=brand2, category=category,
                                       slug='samsung-galaxy-s24')
    product3 = Products.objects.create(name="iPhone 16 Pro Max", brand=Brands.objects.create(name="Apple"),
                                       category=category, slug='iphone-16-pro-max')

    Characteristics.objects.create(product=product1, color='красный', built_in_memory=1024, random_access_memory=16,
                                   main_camera=50)
    Characteristics.objects.create(product=product2, color='мятный', built_in_memory=128, random_access_memory=8,
                                   main_camera=50)
    Characteristics.objects.create(product=product3, color='красный', built_in_memory=256, random_access_memory=8,
                                   main_camera=48)

    url = reverse("products:index", kwargs={'category_slug': 'smartphones'})

    response = client.get(url, {'select_brand': ['Huawei', 'Samsung']})

    content = response.content.decode()
    assert product1.name in content
    assert product2.name in content
    assert product3.name not in content


def test_product_view(client, sample_product):
    url = reverse('products:product', kwargs={'product_slug': 'huawei-mate-x6'})
    response = client.get(url)
    assert response.status_code == 200
    assert b'Huawei Mate X6' in response.content
