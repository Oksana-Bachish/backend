from functools import reduce
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
import operator
from django.db.models import Q

from products.models import Products, PRODUCT_SEARCH_VECTOR


def q_search(query, category_slug):
    if query.isdigit() and len(query) <= 5:
        return Products.objects.filter(id=int(query))

    vector = SearchVector('name', 'description')
    query = SearchQuery(query)

    return Products.objects\
        .annotate(rank=SearchRank(vector, query))\
        .filter(Q(rank__gt=0.01), Q(category__slug=category_slug))\
        .order_by('-rank')  # рассчитывает, насколько совпадает информация с запросом


def ai_product_search(user_query: str, limit: int = 15) -> list[dict]:
    """ Подбирает релевантные товары для ИИ-консультанта"""
    base_qs = Products.objects.filter(quantity__gt=0).only('id', 'name', 'price')
    vector = PRODUCT_SEARCH_VECTOR

    words = [w for w in user_query.split() if len(w) >= 3][:10]
    if words:
        search_query = reduce(
            operator.or_,
            (SearchQuery(word, config='russian') for word in words)
        )
        db_products = list(
            base_qs.annotate(search=vector)
            .filter(search=search_query)
            .annotate(rank=SearchRank(vector, search_query))
            .order_by('-rank')[:limit]
        )
    else:
        db_products = []

    if not db_products:
        db_products = list(
            base_qs.filter(category__name__in=["Смартфоны", "Ноутбуки", "Планшеты"])[:limit]
        )

    return [
        {'id': p.id, 'name': p.name, 'price': float(p.price)}
        for p in db_products
    ]

