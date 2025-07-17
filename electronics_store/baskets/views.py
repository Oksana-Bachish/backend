from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.views import View

from baskets.mixins import BasketMixin
from baskets.models import Basket
from baskets.utils import get_user_baskets
from products.models import Products


class BasketAddView(BasketMixin, View):
    def post(self, request):
        product_id = request.POST.get('product_id')
        product = Products.objects.get(id=product_id)

        basket = self.get_basket(request, product=product)
        if basket:
            basket.quantity += 1
            basket.save()
        else:
            Basket.objects.create(user=request.user if request.user.is_authenticated else None,
                                  session_key=request.session.session_key if not request.user.is_authenticated else None,
                                  product=product, quantity=1)  # если у пользователя нет данного товара, то создаем корзину
        response_data = {
            'message': 'Товар добавлен в корзину',
            'basket_items_html': self.render_basket(request)
        }
        return JsonResponse(response_data)


class BasketChangeView(BasketMixin, View):
    def post(self, request):
        basket_id = request.POST.get('basket_id')
        basket = self.get_basket(request, basket_id=basket_id)

        basket.quantity = request.POST.get('quantity')
        basket.save()

        quantity = basket.quantity

        response_data = {
            'message': 'Количество изменено',
            'quantity': quantity,
            'basket_items_html': self.render_basket(request),
        }

        return JsonResponse(response_data)


class BasketRemoveView(BasketMixin, View):
    def post(self, request):
        basket_id = request.POST.get('basket_id')
        basket = self.get_basket(request, basket_id=basket_id)

        quantity = basket.quantity
        basket.delete()

        response_data = {
            'message': 'Товар удален из корзины',
            'basket_items_html': self.render_basket(request),
            'quantity_deleted': quantity
        }
        return JsonResponse(response_data)


# Функциональные представления

# def basket_add(request):
#     product_id = request.POST.get('product_id')
#     product = Products.objects.get(id=product_id)
#     if request.user.is_authenticated:
#         baskets = Basket.objects.filter(user=request.user, product=product)  # корзины которые есть у пользователя по конкретному продукту
#
#         if baskets.exists():  # если у пользователя есть уже данный товар в корзине, то увеличиваем количество
#             basket = baskets.first()
#             if basket:
#                 basket.quantity += 1
#                 basket.save()
#         else:
#             Basket.objects.create(user=request.user, product=product, quantity=1)  # если у пользователя нет данного товара, то создаем корзину
#     else:
#         baskets = Basket.objects.filter(session_key=request.session.session_key, product=product)
#         if baskets.exists():
#             basket = baskets.first()
#             if basket:
#                 basket.quantity += 1
#                 basket.save()
#         else:
#             Basket.objects.create(session_key=request.session.session_key, product=product, quantity=1)
#
#
#     # return redirect(request.META['HTTP_REFERER'])  # перенаправляемся на страницу, с которой попали в корзину
#
#     user_baskets = get_user_baskets(request)
#     basket_items_html = render_to_string('baskets/includes/included_basket.html', {'baskets': user_baskets}, request=request)
#
#     response_data = {
#         'message': 'Товар добавлен в корзину',
#         'basket_items_html': basket_items_html
#     }
#     return JsonResponse(response_data)


# def basket_change(request):
#     basket_id = request.POST.get('basket_id')
#     quantity = request.POST.get('quantity')
#
#     basket = Basket.objects.get(id=basket_id)
#
#     basket.quantity = quantity
#     basket.save()
#     updated_quantity = basket.quantity
#
#     user_basket = get_user_baskets(request)
#
#     context = {'baskets': user_basket}
#
#     referer = request.META.get('HTTP_REFERER')
#     if reverse('orders:create_order') in referer:
#         context["orders"] = True
#
#     basket_items_html = render_to_string('baskets/includes/included_basket.html', context, request=request)
#
#     response_data = {
#         'message': 'Количество изменено',
#         'basket_items_html': basket_items_html,
#         'quantity': updated_quantity
#     }
#     return JsonResponse(response_data)


# def basket_remove(request):
#     basket_id = request.POST.get('basket_id')
#     basket = Basket.objects.get(id=basket_id)
#     quantity = basket.quantity
#     basket.delete()
#
#     user_basket = get_user_baskets(request)
#
#     context = {'baskets': user_basket}
#
#     referer = request.META.get('HTTP_REFERER')
#     if reverse('orders:create_order') in referer:
#         context["orders"] = True
#
#     basket_items_html = render_to_string('baskets/includes/included_basket.html', context,
#                                          request=request)  # преобразуем в строку
#     response_data = {
#         'message': 'Товар удален',
#         'basket_items_html': basket_items_html,
#         'quantity_deleted': quantity
#     }
#     return JsonResponse(response_data)