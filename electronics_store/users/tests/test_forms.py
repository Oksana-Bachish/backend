import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

from unittest.mock import patch

from users.forms import UserLoginForm, UserRegistrationForm, ProfileForm
from users.forms import CeleryPasswordResetForm
from users.models import User

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


@pytest.mark.django_db
def test_celery_password_reset_form_sends_task():
    user = User.objects.create_user(username='testuser', email='user@example.com', password='password123')

    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    with patch('users.forms.send_password_reset_email_task.delay') as mock_delay:
        context = {
            'user': user,
            'url': 'http://test.com',
            'uid': uidb64,
            'uidb64': uidb64,
            'token': token,
        }

        form = CeleryPasswordResetForm()

        form.send_mail(
            subject_template_name='users/password_reset_form.html',
            email_template_name='users/password_reset_email.html',
            context=context,
            from_email='webmaster@localhost',
            to_email=user.email
        )

        assert mock_delay.call_count == 1
        kwargs = mock_delay.call_args.kwargs
        assert kwargs['from_email'] == 'webmaster@localhost'
        assert kwargs['recipient_list'] == [user.email]
        assert 'subject' in kwargs
        assert 'message' in kwargs
