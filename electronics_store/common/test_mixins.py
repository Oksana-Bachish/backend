import pytest
from django.core.cache import cache
from common.mixins import CacheMixin


@pytest.mark.django_db
def test_set_get_cache_when_empty():
    mixin = CacheMixin()
    cache_name = 'test_cache'
    cache_time = 60
    query = {'data': 123}

    # убедимся, что кэш пуст
    cache.delete(cache_name)

    result = mixin.set_get_cache(query, cache_name, cache_time)

    assert result == query
    assert cache.get(cache_name) == query


def test_set_get_cache_when_exists():
    mixin = CacheMixin()
    cache_name = 'test_cache'
    cache_time = 60
    query = {'data': 123}

    # сначала положим данные в кэш
    cache.set(cache_name, {'data': 'old'}, cache_time)

    result = mixin.set_get_cache(query, cache_name, cache_time)

    # должно вернуть старое значение, а не query
    assert result == {'data': 'old'}
