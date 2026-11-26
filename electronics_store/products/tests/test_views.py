import pytest
import json
import requests
from unittest.mock import patch, MagicMock
from django.urls import reverse
from django.core.cache import cache

from products.views import FALLBACK_UI_RESPONSE
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


@pytest.fixture(autouse=True)
def clear_django_cache():
    """Очистка кэша до и после каждого теста для изоляции rate-лимитера."""
    cache.clear()
    yield
    cache.clear()


@pytest.mark.django_db
@patch('requests.post')
def test_ai_consultant_view_success(mock_post, client, sample_product):
    """Успешный сценарий: сбор RAG-контекста из БД и проксирование ответа от FastAPI."""

    # Настройка mock-ответа от FastAPI микросервиса
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'status': 'success', 'response': 'Рекомендую этот смартфон! 📱'}
    mock_post.return_value = mock_response

    # Имитация запроса от фронтенда
    url = reverse('products:ai_consultant')
    payload = {'message': 'Посоветуй телефон'}

    response = client.post(
        url,
        data=json.dumps(payload),
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
    assert called_kwargs['timeout'] == 20

    # Валидация структуры передаваемых данных (RAG контекст)
    sent_json = called_kwargs['json']
    assert sent_json['query'] == 'Посоветуй телефон'
    assert len(sent_json['products']) == 1
    assert sent_json['products'][0]['name'] == 'Huawei Mate X6'


@pytest.mark.django_db
@patch('requests.post')
def test_ai_consultant_view_timeout_graceful_degradation(mock_post, client):
    """Graceful degradation: при таймауте FastAPI возвращается резервный ответ без 500-й ошибки."""
    mock_post.side_effect = requests.exceptions.Timeout('Connection timed out')

    url = reverse('products:ai_consultant')
    payload = {'message': 'Посоветуй телефон'}

    response = client.post(
        url,
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == 200
    json_data = response.json()
    assert json_data['status'] == 'success'
    assert json_data['response'] == FALLBACK_UI_RESPONSE


@pytest.mark.django_db
@patch('requests.post')
def test_ai_consultant_view_rate_limit(mock_post, client):
    """Защита от ботов: запросы сверх лимита (5/мин с одного IP) блокируются до вызова LLM."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'status': 'success', 'response': 'Ок'}
    mock_post.return_value = mock_response

    url = reverse('products:ai_consultant')
    payload = {'message': 'Посоветуй ноутбук'}

    # Первые 5 запросов проходят в рамках лимита
    for _ in range(5):
        res = client.post(url, data=json.dumps(payload), content_type='application/json')
        assert res.status_code == 200

    assert mock_post.call_count == 5

    # 6-й запрос отсекается лимитером без обращения к FastAPI
    blocked_res = client.post(url, data=json.dumps(payload), content_type='application/json')
    assert blocked_res.status_code == 200
    assert 'слишком быстро' in blocked_res.json()['response']
    assert mock_post.call_count == 5


@pytest.mark.django_db
@patch('requests.post')
def test_ai_consultant_view_too_long_query(mock_post, client):
    """Защита от абуза: запросы длиннее 500 символов отклоняются на уровне валидации."""
    url = reverse('products:ai_consultant')
    payload = {'message': 'A' * 501}

    response = client.post(
        url,
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == 200
    assert 'до 500 символов' in response.json()['response']
    assert not mock_post.called


@pytest.mark.django_db
@patch('requests.post')
def test_ai_consultant_view_short_words_and_forwarded_ip(mock_post, client, sample_product):
    """Покрытие: заголовок X-Forwarded-For, короткие слова (<3 символов) и фолбэк-каталог."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'status': 'success', 'response': 'Посмотрите наши популярные модели!'}
    mock_post.return_value = mock_response

    url = reverse('products:ai_consultant')

    response = client.post(
        url,
        data=json.dumps({'message': 'ну ок'}),
        content_type='application/json',
        HTTP_X_FORWARDED_FOR='203.0.113.50, 10.0.0.1',
    )

    assert response.status_code == 200
    assert response.json()['response'] == 'Посмотрите наши популярные модели!'
    assert mock_post.called


@pytest.mark.django_db
@patch('requests.post')
def test_ai_consultant_view_fastapi_error_and_invalid_json(mock_post, client):
    """Покрытие: ответ FastAPI != 200 и перехват непредвиденных исключений (битый JSON)."""
    url = reverse('products:ai_consultant')

    # 1. FastAPI вернул статус 500
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_post.return_value = mock_response

    res_500 = client.post(url, data=json.dumps({'message': 'Посоветуй ноутбук'}), content_type='application/json')
    assert res_500.status_code == 200
    assert res_500.json()['response'] == FALLBACK_UI_RESPONSE

    # 2. Битый JSON в теле запроса
    res_bad_json = client.post(url, data='{broken_json', content_type='application/json')
    assert res_bad_json.status_code == 200
    assert res_bad_json.json()['response'] == FALLBACK_UI_RESPONSE


@pytest.mark.django_db
def test_ai_consultant_view_validation_and_method(client):
    """Покрытие: запрещенный метод GET и слишком короткий запрос (<2 символов)."""
    url = reverse('products:ai_consultant')

    get_res = client.get(url)
    assert get_res.status_code == 405

    short_res = client.post(url, data=json.dumps({'message': 'a'}), content_type='application/json')
    assert short_res.status_code == 200
    assert 'минимум 2 символа' in short_res.json()['response']
