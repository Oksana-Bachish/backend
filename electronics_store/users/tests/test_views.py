import pytest
from decimal import Decimal
from django.urls import reverse
from django.contrib.messages import get_messages
from users.models import User
from products.models import Products, Categories, Brands
from baskets.models import Basket


@pytest.fixture
def user(db):
    return User.objects.create_user(username='testuser', password='12345')


@pytest.fixture
def product(db):
    category = Categories.objects.create(name='Смартфоны', slug='smartphones')
    brand = Brands.objects.create(name='Test brand', slug='test-brand')
    return Products.objects.create(name='Test product', brand=brand, category=category, price=Decimal('1000.00'),
                                   quantity=3, slug='test_product')


@pytest.fixture
def basket(user, product):
    return Basket.objects.create(user=user, product=product, quantity=2)


@pytest.mark.django_db
def test_user_login_view(client, user):
    session = client.session
    session.save()

    url = reverse('users:login')
    response = client.post(url, {'username': 'testuser', 'password': '12345'}, follow=True)

    assert response.status_code == 200
    assert response.wsgi_request.user.is_authenticated

    messages = list(get_messages(response.wsgi_request))
    assert any('Вы вошли в аккаунт' in str(m.message) for m in messages)


@pytest.mark.django_db
def test_login_redirect_to_next(client, user):
    url = reverse('users:login')
    next_url = reverse('users:profile')
    response = client.post(url, {
        'username': 'testuser',
        'password': '12345',
        'next': next_url
    }, follow=True)
    assert response.status_code == 200
    assert response.request['PATH_INFO'] == next_url


@pytest.mark.django_db
def test_login_transfers_basket_items(client, user, product):
    session = client.session
    Basket.objects.create(session_key=session.session_key, product=product, quantity=2)
    session.save()

    client.post(reverse('users:login'), {
        'username': 'testuser',
        'password': '12345'
    }, follow=True)

    assert Basket.objects.filter(user=user).exists()


@pytest.mark.django_db
def test_registration_transfers_basket_items(client, product):
    session = client.session
    session.save()

    Basket.objects.create(session_key=session.session_key, product=product, quantity=1)

    username = 'newuser'

    client.post(reverse('users:registration'), {
        'first_name': 'first',
        'last_name': 'last',
        'username': username,
        'password1': 'ComplexPass123',
        'password2': 'ComplexPass123',
        'email': 'test@example.com'
    }, follow=True)

    created_user = User.objects.get(username=username)
    assert Basket.objects.filter(user=created_user).exists()


@pytest.mark.django_db
def test_user_registration_view(client, user):
    url = reverse('users:registration')
    response = client.post(url, {
        'first_name': 'new_first_name',
        'last_name': 'new_last_name',
        'username': 'newuser',
        'password1': 'ComplexPass123',
        'password2': 'ComplexPass123',
        'email': 'test@example.com'
    }, follow=True)

    assert response.status_code == 200
    created_user = User.objects.get(username='newuser')
    assert created_user.is_authenticated
    assert response.wsgi_request.user == created_user
    messages = list(get_messages(response.wsgi_request))
    assert any('Вы успешно зарегистрированы' in str(m.message) for m in messages)


@pytest.mark.django_db
def test_user_profile_access_requires_login(client):
    url = reverse('users:profile')
    response = client.get(url)
    assert response.status_code == 302
    login_url = reverse('users:login')
    assert response.url.startswith(login_url)


@pytest.mark.django_db
def test_user_profile_update(client):
    user = User.objects.create_user(first_name='Ivan', last_name='Ivanov', username='testuser', password='12345',
                                         email='test@mail.ru')
    client.login(username='testuser', password='12345')
    url = reverse('users:profile')
    response = client.post(url, {
        'username': 'testuser',
        'first_name': 'Ivan',
        'last_name': 'Ivanov',
        'email': 'update_test@mail.ru',
    }, follow=True)
    user.refresh_from_db()
    assert user.first_name == 'Ivan'
    assert user.email == 'update_test@mail.ru'
    messages = list(get_messages(response.wsgi_request))
    assert any('Профайл успешно создан' in str(m.message) for m in messages)


@pytest.mark.django_db
def test_profile_form_invalid(client, user):
    client.login(username='testuser', password='12345')
    url = reverse('users:profile')
    # Некорректный email
    response = client.post(url, {
        'username': 'testuser',
        'first_name': 'Ivan',
        'last_name': 'Ivanov',
        'email': 'invalid_email'
    }, follow=True)

    messages = list(get_messages(response.wsgi_request))
    assert any('Произошла ошибка' in str(m.message) for m in messages)
    assert response.status_code == 200


@pytest.mark.django_db
def test_users_cart_view(client):
    url = reverse('users:users_cart')
    response = client.get(url)
    assert response.status_code == 200
    assert 'Electronics_store - Корзина' in response.content.decode()


@pytest.mark.django_db
def test_user_logout(client, user):
    client.login(username='testuser', password='12345')
    url = reverse('users:logout')
    response = client.get(url, follow=True)

    assert response.status_code == 200
    assert not response.wsgi_request.user.is_authenticated
    messages = list(get_messages(response.wsgi_request))
    assert any('Вы вышли из аккаунта' in str(m.message) for m in messages)