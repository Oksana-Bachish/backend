import pytest
from django.test import RequestFactory
from django.urls import reverse
from django.contrib.sessions.middleware import SessionMiddleware
from main.views import IndexView, AboutView, DeliveryInfView, ContactsInfView
from users.models import User


def add_session_to_request(request):
    middleware = SessionMiddleware(get_response=lambda r: None)
    middleware.process_request(request)
    request.session.save()
    return request


@pytest.mark.django_db
@pytest.mark.parametrize('url_name, view_class, template_name, expected_context', [
    ('main:index', IndexView, 'main/index.html',
     {'title': 'Electronics - Главная страница', 'content': 'Магазин современных гаджетов Electronics'}),
    ('main:about', AboutView, 'main/about.html',
     {'title': 'Про нас', 'content': 'Про нас',
      'text_on_page': ('На сегодняшний день нашему магазину уже более двух лет. '
                       'У нас представлена вся линейка гаджетов и аксессуаров, где каждый сможет найти что-то для себя. '
                       'Мы продаем только оригинальные товары с гарантией качества и можем гордиться таким ценным доверием наших '
                       'покупателей. Мы работаем 7 дней в неделю, без обедов и выходных!')}),
    ('main:delivery', DeliveryInfView, 'main/delivery.html', {'title': 'Доставка и оплата'}),
    ('main:contacts', ContactsInfView, 'main/contacts.html', {'title': 'Контакты'})
])
def test_template_views_rf(url_name, view_class, template_name, expected_context):
    factory = RequestFactory()
    request = factory.get(reverse(url_name))
    user = User.objects.create_user(username='testuser', password='12345', first_name='Иван', last_name='Иванов')
    request.user = user

    request = add_session_to_request(request)

    response = view_class.as_view()(request)
    response.render()

    for key, value in expected_context.items():
        assert response.context_data[key] == value

    assert response.status_code == 200






