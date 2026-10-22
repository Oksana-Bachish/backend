import pytest
from django.core import mail
from django.conf import settings
from unittest.mock import patch
from celery.exceptions import Retry

from users.tasks import send_password_reset_email_task

def test_send_password_reset_email_task_success():
    mail.outbox.clear()

    send_password_reset_email_task(
        subject='Сброс пароля',
        message='Перейдите по ссылке...',
        from_email=None,
        recipient_list=['customer@example.com']
    )

    assert len(mail.outbox) == 1

    send_email = mail.outbox[0]
    assert send_email.subject == 'Сброс пароля'
    assert send_email.to == ['customer@example.com']
    assert send_email.from_email == settings.DEFAULT_FROM_EMAIL


@patch('users.tasks.send_password_reset_email_task.retry', side_effect=Retry)
@patch('users.tasks.send_mail', side_effect=Exception("Яндекс упал!"))
def test_task_retries_on_exception(mock_send_mail, mock_retry):
    """Проверяем авторетрай таски при ошибке"""
    with pytest.raises(Retry):
        send_password_reset_email_task(
            subject='Тест', message='Тест', from_email='1@1.com', recipient_list=['2@2.com']
        )

    assert mock_retry.called