from django.urls import path
from payment import views

app_name = 'payment'

urlpatterns = [
    path('process/', views.payment_process, name='process'),
    path('completed/', views.PaymentCompletedView.as_view(), name='completed'),
    path('canceled/', views.PaymentCanceledView.as_view(), name='canceled'),
]
