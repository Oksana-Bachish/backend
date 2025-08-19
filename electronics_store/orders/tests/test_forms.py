import pytest
from orders.forms import CreateOrderForm


@pytest.mark.parametrize("form_data, is_valid", [
    ({"first_name": "Иван", "last_name": "Иванов", "phone_number": "1234567890",
      "requires_delivery": "1", "delivery_address": "ул. Ленина, 10", "payment_on_get": "0"}, True),

    ({"first_name": "Петр", "last_name": "Петров", "phone_number": "12345abcde",
      "requires_delivery": "0", "delivery_address": "", "payment_on_get": "1"}, False),

    ({"first_name": "Анна", "last_name": "Сидорова", "phone_number": "123456789",  # 9 цифр, ошибка
      "requires_delivery": "1", "delivery_address": "ул. Пушкина", "payment_on_get": "0"}, False),

    ({"first_name": "Мария", "last_name": "Кузнецова", "phone_number": "0987654321",
      "requires_delivery": "0", "payment_on_get": "1"}, True),  # без адреса — delivery_address не обязателен
])


def test_create_order_form_validation(form_data, is_valid):
    form = CreateOrderForm(data=form_data)
    assert form.is_valid() == is_valid

    if not is_valid:
        assert 'phone_number' in form.errors
    else:
        # Если форма валидна, cleaned_data должна содержать phone_number
        assert 'phone_number' in form.cleaned_data


def test_clean_phone_number_valid():
    form = CreateOrderForm(data={
        "first_name": "Иван",
        "last_name": "Иванов",
        "phone_number": "1234567890",
        "requires_delivery": "1",
        "delivery_address": "ул. Ленина, 10",
        "payment_on_get": "0",
    })
    assert form.is_valid()
    assert form.cleaned_data['phone_number'] == '1234567890'


@pytest.mark.parametrize('phone_number', [
    "12345abcde",  # буквы
    "123456789",  # 9 цифр
    "12345678901",  # 11 цифр
    "abcdefghij",  # все буквы
    ""  # пустая строка
])
def test_clean_phone_number_invalid(phone_number):
    form = CreateOrderForm(data={
        "first_name": "Иван",
        "last_name": "Иванов",
        "phone_number": phone_number,
        "requires_delivery": "0",
        "payment_on_get": "1",
    })
    assert not form.is_valid()
    assert 'phone_number' in form.errors


@pytest.mark.parametrize('requires_delivery, expected', [
    ('0', False),
    ('1', True),
])
def test_requires_delivery_field_mapping(requires_delivery, expected):
    form = CreateOrderForm(data={
        "first_name": "Иван",
        "last_name": "Иванов",
        "phone_number": "1234567890",
        "requires_delivery": requires_delivery,
        "payment_on_get": "0",
    })
    assert form.is_valid()
    assert form.cleaned_data['requires_delivery'] == requires_delivery


@pytest.mark.parametrize('payment_on_get, expected', [
    ('0', '0'),
    ('1', '1')
])
def test_payment_on_get_failed(payment_on_get, expected):
    form = CreateOrderForm(data={
        "first_name": "Иван",
        "last_name": "Иванов",
        "phone_number": "1234567890",
        "requires_delivery": "0",
        "payment_on_get": payment_on_get,
    })
    assert form.is_valid()
    assert form.cleaned_data['payment_on_get'] == expected
