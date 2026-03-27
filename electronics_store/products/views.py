from django.core.paginator import Paginator
from django.db.models import Q
from django.core.cache import cache
from django.http import Http404
from django.shortcuts import render
from django.views.generic import DetailView, ListView

from products.models import Products
from products.utils import q_search


class CatalogView(ListView):
    model = Products
    template_name = 'products/catalog.html'
    context_object_name = 'products'
    paginate_by = 6
    slug_url_kwarg = "category_slug"

    def get_queryset(self):
        category_slug = self.kwargs.get(self.slug_url_kwarg)
        on_sale = self.request.GET.get('on_sale', None)
        order_by = self.request.GET.get('order_by', None)
        query = self.request.GET.get('q', None)
        brand = self.request.GET.getlist('select_brand', None)
        color = self.request.GET.getlist('select_color', None)
        build_memory = self.request.GET.getlist('select_build_memory', None)
        access_memory = self.request.GET.getlist('select_access_memory', None)
        main_camera = self.request.GET.getlist('select_main_camera', None)

        cache_key = f"catalog_{category_slug}_{brand}_{color}_{build_memory}_{access_memory}_{main_camera}_{on_sale}_{order_by}_{query}"
        cache_queryset = cache.get(cache_key)
        if cache_queryset:
            return cache_queryset

        q_objects = Q()
        if brand:
            q_objects &= Q(brand__name__in=brand)
        if color:
            q_objects &= Q(characteristics__color__in=color)
        if build_memory:
            q_objects &= Q(characteristics__built_in_memory__in=build_memory)
        if build_memory:
            q_objects &= Q(characteristics__built_in_memory__in=build_memory)
        if access_memory:
            q_objects &= Q(characteristics__random_access_memory__in=access_memory)
        if main_camera:
            q_objects &= Q(characteristics__main_camera__in=main_camera)
        q_objects &= Q(category__slug=category_slug)

        products = super().get_queryset().select_related('brand', 'category', 'characteristics')\
            .prefetch_related('images').filter(q_objects)

        if query:
            products = q_search(query, category_slug)

        if on_sale:
            products = products.filter(discount__gt=0)
        if order_by and order_by != 'default':
            products = products.order_by(order_by)

        cache.set(cache_key, products, timeout=60 * 5)

        return products

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Купить технику'
        context['category_slug'] = self.kwargs.get('category_slug')
        return context


class ProductView(DetailView):
    template_name = 'products/product.html'
    slug_url_kwarg = 'product_slug'
    context_object_name = 'product'

    def get_object(self, queryset=None):
        product_slug = self.kwargs.get(self.slug_url_kwarg)

        cache_key = f'product_{product_slug}'
        product = cache.get(cache_key)

        if not product:
            product = Products.objects.select_related('brand', 'category', 'characteristics')\
                .prefetch_related('images')\
                .get(slug=self.kwargs.get('product_slug'))
            cache.set(cache_key, product, 600)

        return product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.name
        return context



# Функциональные представления

# def catalog(request, category_slug=None):
#     page = request.GET.get('page', 1)
#     on_sale = request.GET.get('on_sale', None)
#     order_by = request.GET.get('order_by', None)
#     query = request.GET.get('q', None)
#     brand = request.GET.getlist('select_brand', None)
#     color = request.GET.getlist('select_color', None)
#     build_memory = request.GET.getlist('select_build_memory', None)
#     access_memory = request.GET.getlist('select_access_memory', None)
#     main_camera = request.GET.getlist('select_main_camera', None)
#
#     q_objects = Q()
#     if brand:
#         q_objects &= Q(brand__name__in=brand)
#     if color:
#         q_objects &= Q(characteristics__color__in=color)
#     if build_memory:
#         q_objects &= Q(characteristics__built_in_memory__in=build_memory)
#     if build_memory:
#         q_objects &= Q(characteristics__built_in_memory__in=build_memory)
#     if access_memory:
#         q_objects &= Q(characteristics__random_access_memory__in=access_memory)
#     if main_camera:
#         q_objects &= Q(characteristics__main_camera__in=main_camera)
#     q_objects &= Q(category__slug=category_slug)
#
#     products = Products.objects.filter(q_objects)
#
#     if query:
#         products = q_search(query, category_slug)
#
#     if on_sale:
#         products = products.filter(discount__gt=0)
#     if order_by and order_by != 'default':
#         products = products.order_by(order_by)
#
#     paginator = Paginator(products, 3)
#     current_page = paginator.page(int(page))
#
#     context = {
#         'title': 'Купить мобильный телефон',
#         #'brands': brands,
#         'products': current_page,
#         'category_slug': category_slug,
#     }
#
#     return render(request, 'products/catalog.html', context)


# def product(request, product_slug):
#     product = Products.objects.get(slug=product_slug)
#
#     context = {
#         'product': product
#     }
#     return render(request, 'products/product.html', context)
