from django.db import models

from products.models import Products
from users.models import User


class BasketQuerySet(models.QuerySet):
    def total_price(self):
        return sum(basket.product_price() for basket in self)

    def total_quantity(self):
        if self:
            return sum(basket.quantity for basket in self)
        return 0


class Basket(models.Model):
    user = models.ForeignKey(to=User, blank=True, null=True, on_delete=models.CASCADE, verbose_name='Пользователь')
    product = models.ForeignKey(to=Products, on_delete=models.CASCADE, verbose_name='Товар')
    quantity = models.PositiveSmallIntegerField(default=0, verbose_name='Количество')
    session_key = models.CharField(max_length=32, null=True, blank=True)
    created_timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    class Meta:
        db_table = 'basket'
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        ordering = ('id',)

    objects = BasketQuerySet().as_manager()

    def product_price(self):
        price = self.product.sell_price().replace(" ", "")
        return round(int(price) * self.quantity, 2)

    def __str__(self):
        if self.user:
            return f'Корзина {self.user.username} | Товар {self.product.name} | Количество {self.quantity}'
        return f'Анонимная корзина | Товар {self.product.name} | Количество {self.quantity}'
