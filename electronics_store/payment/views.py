from django.shortcuts import render, redirect, get_object_or_404
from decimal import Decimal, ROUND_HALF_UP
from django.urls import reverse
from django.views.generic import TemplateView, FormView
from django.conf import settings
import stripe

from orders.models import Order, OrderItem
from payment.forms import PaymentForm

stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION


class PaymentProcessView(FormView):
    template_name = 'payment/process.html'
    form_class = PaymentForm

    def get_order_and_items(self):
        order_id = self.request.session.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        order_items = OrderItem.objects.filter(order__id=order_id)
        return order, order_items

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order, order_items = self.get_order_and_items()
        context['order'] = order
        context['order_items'] = order_items
        return context

    def form_valid(self, form):
        print("form_valid called")
        order, order_items = self.get_order_and_items()

        success_url = self.request.build_absolute_uri(reverse('payment:completed'))
        cancel_url = self.request.build_absolute_uri(reverse('payment:canceled'))

        session_data = {
            'mode': 'payment',
            'client_reference_id': order.id,
            'success_url': success_url,
            'cancel_url': cancel_url,
            'line_items': [],
            'payment_method_types': ['card'],
        }

        for item in order_items:
            unit_price = (item.price / item.quantity).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            session_data['line_items'].append({
                'price_data': {
                    'unit_amount': int(unit_price * Decimal('100')),
                    'currency': 'RUB',
                    'product_data': {
                        'name': item.product.name,
                    },
                },
                'quantity': item.quantity
            })

        session = stripe.checkout.Session.create(**session_data)
        return redirect(session.url, code=303)


class PaymentCompletedView(TemplateView):
    template_name = 'payment/completed.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Оплата прошла успешно'
        return context


class PaymentCanceledView(TemplateView):
    template_name = 'payment/canceled.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Платеж отменен'
        return context


# def payment_process(request):
#     order_id = request.session.get('order_id', None)
#     order = get_object_or_404(Order, id=order_id)
#     order_items = OrderItem.objects.filter(order__id=order_id)
#
#     if request.method == 'POST':
#         success_url = request.build_absolute_uri(reverse('payment:completed'))
#         cancel_url = request.build_absolute_uri(reverse('payment:canceled'))
#         session_data = {
#             'mode': 'payment',
#             'client_reference_id': order.id,
#             'success_url': success_url,
#             'cancel_url': cancel_url,
#             'line_items': []
#         }
#         for item in order_items:
#             discounted_price = item.products_price()
#             session_data['line_items'].append(
#                 {'price_data': {
#                     'unit_amount': int(discounted_price * Decimal('100')),
#                     'currency': 'RUB',
#                     'product_data': {
#                         'name': item.product.name,
#                     }, },
#                     'quantity': item.quantity})
#         session = stripe.checkout.Session.create(**session_data)
#         return redirect(session.url, code=303)
#     else:
#         return render(request, 'payment/process.html', locals())