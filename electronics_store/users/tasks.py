from django.core.mail import send_mail
from celery import shared_task
from django.conf import settings


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={'max_retries': 5},
)
def send_password_reset_email_task(self, subject, message, from_email, recipient_list,
                                   html_message=None):
    sender = from_email or settings.DEFAULT_FROM_EMAIL
    send_mail(
        subject=subject,
        message=message,
        from_email=sender,
        recipient_list=recipient_list,
        html_message=html_message,
        fail_silently=False,
    )
