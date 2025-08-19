import pytest
from products.models import Products, Brands, Categories
from products.utils import q_search


@pytest.mark.django_db
def test_q_search_by_id():
    category = Categories.objects.create(name='Смартфоны', slug='smartphones')
    brand = Brands.objects.create(name='TestBrand', slug='testbrand')
    product = Products.objects.create(id=123, name='Test Product', description="Описание тестового продукта",
                                      price=40000.00, brand=brand, category=category)
    result = q_search('123', 'smartphones')
    assert list(result) == [product]


@pytest.mark.django_db
def test_q_search_text_search():
    category = Categories.objects.create(name='Планшеты', slug='tablets')
    brand = Brands.objects.create(name='BrandX', slug='brandx')
    product1 = Products.objects.create(name='Apple iPad', description="Планшет от Apple",
                                      price=70000.00, brand=brand, category=category)
    product2 = Products.objects.create(name='Samsung Galaxy Tab', description="Планшет от Samsung",
                                      price=50000.00, brand=brand, category=category)
    result = q_search("Apple", "tablets")
    assert product1 in result
    assert product2 not in result


@pytest.mark.django_db
def test_q_search_with_wrong_category():
    cat1 = Categories.objects.create(name='Смартфоны', slug='smartphones')
    cat2 = Categories.objects.create(name='Планшеты', slug='tablets')
    brand = Brands.objects.create(name='BrandY', slug='brandy')
    product = Products.objects.create(name='Xiaomi Redmi', description="Смартфон Xiaomi",
                                      price=30000.00, brand=brand, category=cat1)
    result = q_search('Xiaomi', 'tablets')
    assert not result.exists()
