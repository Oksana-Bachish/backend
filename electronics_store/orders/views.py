from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView

from baskets.models import Basket
from orders.forms import CreateOrderForm
from orders.models import Order, OrderItem
from products.models import Products


class CreateOrderView(LoginRequiredMixin, FormView):
    template_name = 'orders/create_order.html'
    form_class = CreateOrderForm
    success_url = reverse_lazy('users:profile')

    def get_initial(self):
        initial = super().get_initial()
        initial['first_name'] = self.request.user.first_name
        initial['last_name'] = self.request.user.last_name
        return initial

    def form_valid(self, form):
        try:
            with transaction.atomic():  # атомарная транзакция. Сохраняется все или ничего
                user = self.request.user
                basket_items = Basket.objects.filter(user=user)

                if basket_items.exists():  # если корзины существуют
                    # Создать заказ
                    order = Order.objects.create(
                        user=user,
                        phone_number=form.cleaned_data['phone_number'],
                        requires_delivery=form.cleaned_data['requires_delivery'],
                        delivery_address=form.cleaned_data['delivery_address'],
                        payment_on_get=form.cleaned_data['payment_on_get'],
                    )

                    # Создать заказанные товары
                    for basket_item in basket_items:
                        product = Products.objects.select_for_update().get(id=basket_item.product.id)
                        name = basket_item.product.name
                        price = basket_item.product_price()
                        quantity = basket_item.quantity

                        if product.quantity < quantity:
                            raise ValidationError(f'Недостаточное количество товара "{name}" на складе. '
                                                  f'В наличии - {product.quantity}')

                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            name=name,
                            price=price,
                            quantity=quantity
                        )
                        product.quantity -= quantity
                        product.save()

                    # Очистить корзину пользователя  после создания заказа
                    basket_items.delete()
                    payment_on_get = form.cleaned_data['payment_on_get']

                    if payment_on_get == '0':
                        self.request.session['order_id'] = order.id
                        return redirect(reverse('payment:process'))
                    else:
                        messages.success(self.request, 'Заказ оформлен')
                        return redirect('users:profile')
        except ValidationError as e:  # если будет ошибка ввода данных, то все отменится, ничего не будет сохранено
            messages.success(self.request, str(e))
            return redirect('orders:create_order')

    def form_invalid(self, form):
        messages.error(self.request, 'Заполните все обязательные поля')
        return redirect('orders:create_order')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Electronics Store - Оформление заказа'
        context['order'] = True
        return context



# Функциональные представления

# @login_required
# def create_order(request):
#     if request.method == 'POST':
#         form = CreateOrderForm(data=request.POST)
#         if form.is_valid():
#             try:
#                 with transaction.atomic():  # атомарные транзакции, все происходит в рамках одной транзакции. Проверяется на валидность все поля, если все верно, commit. Если нет, то ничего не сохраняется
#                     user = request.user
#                     basket_items = Basket.objects.filter(user=user)
#
#                     if basket_items.exists():  # если корзины существуют
#                         # Создать заказ
#                         order = Order.objects.create(
#                             user=user,
#                             phone_number=form.cleaned_data['phone_number'],
#                             requires_delivery=form.cleaned_data['requires_delivery'],
#                             delivery_address=form.cleaned_data['delivery_address'],
#                             payment_on_get=form.cleaned_data['payment_on_get'],
#                         )
#
#                         # Создать заказанные товары
#                         for basket_item in basket_items:
#                             product = basket_item.product
#                             name = basket_item.product.name
#                             price = int(basket_item.product.sell_price())
#                             quantity = basket_item.quantity
#
#                             if product.quantity < quantity:
#                                 raise ValidationError(f'Недостаточное количество товара "{name}" на складе. '
#                                                       f'В наличии - {product.quantity}')
#
#                             OrderItem.objects.create(
#                                 order=order,
#                                 product=product,
#                                 name=name,
#                                 price=price,
#                                 quantity=quantity
#                             )
#                             product.quantity -= quantity
#                             product.save()
#
#                         # Очистить корзину пользователя  после создания заказа
#                         basket_items.delete()
#                         payment_on_get = form.cleaned_data['payment_on_get']
#
#                         if payment_on_get == '0':
#                             request.session['order_id'] = order.id
#                             return redirect(reverse('payment:process'))
#                         else:
#                             messages.success(request, 'Заказ оформлен')
#                             return redirect('users:profile')
#             except ValidationError as e:  # если будет ошибка ввода данных, то все отменится, ничего не будет сохранено
#                 messages.success(request, str(e))
#                 return redirect('orders:create_order')
#     else:
#         initial = {
#             'first_name': request.user.first_name,
#             'last_name': request.user.last_name,
#         }
#         form = CreateOrderForm(initial=initial)  # initial - изначальные данные
#
#     context = {
#         'title': 'Electronics Store - Оформление заказа',
#         'form': form,
#         'order': True,
#     }
#
#     return render(request, 'orders/create_order.html', context=context)
