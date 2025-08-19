import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from users.models import User


@pytest.mark.django_db
def test_create_user():
    user = User.objects.create_user(username='testuser', password='testpass123')
    assert user.username == 'testuser'
    assert user.check_password('testpass123')


@pytest.mark.django_db
def test_user_str_method():
    user = User.objects.create_user(username='User1', password='pass123')
    assert str(user) == 'User1'


@pytest.mark.django_db
def test_user_avatar_upload():
    avatar = SimpleUploadedFile(name='avatar.jpg', content=b'someimagecontent', content_type='image/jpeg')
    user = User.objects.create_user(username="avataruser", password="avatarpass", image=avatar)
    assert user.image.name.startswith("users_images/")
    assert 'avatar' in user.image.name


@pytest.mark.django_db
def test_user_phone_number():
    user = User.objects.create_user(username='phoneuser', password='pass123', phone_number='+74956666666')
    assert user.phone_number == '+74956666666'


@pytest.mark.django_db
def test_user_unique_username():
    User.objects.create_user(username="uniqueuser", password="pass1")
    with pytest.raises(Exception):
        User.objects.create_user(username="uniqueuser", password="pass2")
