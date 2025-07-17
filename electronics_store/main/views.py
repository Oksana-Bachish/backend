from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView

from products.models import Brands


class IndexView(TemplateView):
    template_name = 'main/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Electronics - Главная страница'
        context['content'] = 'Магазин современных гаджетов Electronics'
        return context


class AboutView(TemplateView):
    template_name = 'main/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Про нас'
        context['content'] = 'Про нас'
        context['text_on_page'] = 'На сегодняшний день нашему магазину уже более двух лет. У нас представлена вся линейка ' \
                                  'гаджетов и аксессуаров, где каждый сможет найти что-то для себя. Мы продаем только ' \
                                  'оригинальные товары с гарантией качества и можем гордиться таким ценным доверием наших ' \
                                  'покупателей. Мы работаем 7 дней в неделю, без обедов и выходных!'
        return context


class DeliveryInfView(TemplateView):
    template_name = 'main/delivery.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Доставка и оплата'
        return context


class ContactsInfView(TemplateView):
    template_name = 'main/contacts.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Контакты'
        return context



# Функциональные представления

# def index(request):
#     context = {
#         'title': 'Electronics - Главная страница',
#         'content': 'Магазин современных гаджетов Electronics',
#     }
#     return render(request, 'main/index.html', context)


# def about(request):
#     context = {
#         'title': 'О нас',
#         'content': 'О нас',
#         'text_on_page': 'На сегодняшний день нашему магазину уже более двух лет. У нас представлена вся линейка '
#                         'гаджетов и аксессуаров, где каждый сможет найти что-то для себя. Мы продаем только '
#                         'оригинальные товары с гарантией качества и можем гордиться таким ценным доверием наших '
#                         'покупателей. Мы работаем 7 дней в неделю, без обедов и выходных!'
#     }
#     return render(request, 'main/about.html', context)


# def contact(request):
#     context = {
#         'title': 'Контакты',
#     }
#     return render(request, 'main/contacts.html', context)