import pytest
from django.contrib.auth import get_user_model
from users.forms import UserLoginForm, UserRegistrationForm, ProfileForm

UserModel = get_user_model()


def test_user_login_form_field():
    form = UserLoginForm()
    assert 'username' in form.fields
    assert 'password' in form.fields


@pytest.mark.django_db
def test_user_registration_form_valid():
    form = UserRegistrationForm({
        'first_name': 'Ivan',
        'last_name': 'Ivanov',
        'username': 'ivanuser',
        'email': 'ivan@example.com',
        'password1': 'StrongPassword123',
        'password2': 'StrongPassword123'
    })
    assert form.is_valid()


@pytest.mark.django_db
def test_user_registration_form_password_do_not_match():
    form = UserRegistrationForm({
        'first_name': 'Ivan',
        'last_name': 'Ivanov',
        'username': 'ivanuser',
        'email': 'ivan@example.com',
        'password1': 'StrongPassword123',
        'password2': 'OtherPassword456'
    })
    assert not form.is_valid()
    assert 'password2' in form.errors


@pytest.mark.django_db
def test_user_registration_form_empty_fields():
    form = UserRegistrationForm(data={})
    assert not form.is_valid()
    assert 'username' in form.errors
    assert 'password1' in form.errors


@pytest.mark.django_db
def test_profile_form_valid():
    user = UserModel.objects.create(username='testuser', password='12345', email='test@example.com')
    form = ProfileForm(instance=user, data={
        'first_name': 'Updated',
        'last_name': 'Name',
        'username': 'testuser',
        'email': 'new@example.com',
    })
    assert form.is_valid()
