from django import template
from django.utils.http import urlencode

from products.models import Brands, Categories, Products

register = template.Library()


@register.simple_tag()
def tag_brands():
    return Brands.objects.all()


@register.simple_tag()
def tag_products_with_unique_colors():
    return Products.objects.all().order_by('characteristics__color').distinct('characteristics__color')


@register.simple_tag()
def tag_build_memory():
    products = Products.objects.all()
    product = products[0]
    return [i[0] for i in product.characteristics.CHOICE_BUILT_IN_MEMORY]


@register.simple_tag()
def tag_access_memory():
    products = Products.objects.all()
    product = products[0]
    return [i[0] for i in product.characteristics.CHOICE_RANDOM_ACCESS_MEMORY]


@register.simple_tag()
def tag_main_camera():
    products = Products.objects.all()
    product = products[0]
    return [i[0] for i in product.characteristics.CHOICE_MAIN_CAMERA]


@register.simple_tag()
def tag_categories():
    return Categories.objects.all()


@register.simple_tag(takes_context=True)
def change_params(context, **kwargs):
    query = context['request'].GET.dict()
    query.update(kwargs)  # добавляем в словарь номер страницы
    return urlencode(query)  # возвращаем из словаря готовую строку, которую можно ипользовать в URL адресе
