import pytest
import json
import requests
from unittest.mock import patch, MagicMock
from django.urls import reverse
from products.models import Products, Categories, Brands, Characteristics

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


@pytest.mark.django_db
@patch('requests.post')
def test_ai_consultant_view_success(mock_post, client, sample_product):
    """Успешный сценарий: Django собрал товары из БД и успешно вызвал FastAPI"""

    # Настройка mock-ответа от FastAPI микросервиса
    mock_response = MagicMock()
    mock_response.status_code =200
    mock_response.json.return_value = {'status': 'success', 'response': 'Рекомендую этот смартфон! 📱'}
    mock_post.return_value = mock_response

    # Имитация запроса от фронтенда
    url = reverse('products:ai_consultant')
    payload = {'message': 'Посоветуй телефон'}

    response = client.post(
        url,
        data = json.dumps(payload),
        content_type='application/json'
    )

    # Проверка ответа Django View для фронтенда
    assert response.status_code == 200
    json_data = response.json()
    assert json_data['status'] == 'success'
    assert json_data['response'] == 'Рекомендую этот смартфон! 📱'

    # Проверка параметров исходящего запроса к микросервису
    assert mock_post.called
    called_kwargs = mock_post.call_args.kwargs
    assert called_kwargs['timeout'] == 30

    # Валидация структуры передаваемых данных (RAG контекст)
    sent_json = called_kwargs['json']
    assert sent_json['query'] == 'Посоветуй телефон'
    assert len(sent_json['products']) == 1
    assert sent_json['products'][0]['name'] == 'Huawei Mate X6'


@pytest.mark.django_db
@patch('requests.post')
def test_ai_consultant_view_timeout(mock_post, client):
    """Сценарий ошибки: микросервис ИИ завис, и Django выбросил Timeout"""

    # Имитация таймаута сети при запросе к FastAPI
    mock_post.side_effect = requests.exceptions.Timeout('ИИ слишком долго думал')

    url = reverse('products:ai_consultant')
    payload = {'message': 'Посоветуй телефон'}

    response = client.post(
        url,
        data=json.dumps(payload),
        content_type='application/json'
    )

    # Проверка обработки исключения и возврата ошибки 500
    assert response.status_code == 500
    json_data = response.json()
    assert json_data['status'] == 'error'
    assert json_data['message'] == 'ИИ слишком долго думал'
