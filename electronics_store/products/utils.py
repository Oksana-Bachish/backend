from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db.models import Q

from products.models import Products


def q_search(query, category_slug):
    if query.isdigit() and len(query) <= 5:
        return Products.objects.filter(id=int(query))

    vector = SearchVector('name', 'description')
    query = SearchQuery(query)

    return Products.objects.annotate(rank=SearchRank(vector, query)).filter(Q(rank__gt=0.01),
                                                                            Q(category__slug=category_slug)).order_by('-rank')  # рассчитывает, насколько совпадает информация с запросом


