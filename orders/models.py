from django.db import models
from accounts.models import SystemUser
from bid.models import Product


class Order(models.Model):
    """ Модель заказа """
    user = models.ForeignKey(SystemUser, verbose_name="Пользователь", on_delete=models.CASCADE)
    created = models.DateTimeField("Дата создания", auto_now_add=True)
    assembled = models.DateTimeField("Дата комплектовки", null=True, blank=True)
    shipped = models.DateTimeField("Дата отгрузки", null=True, blank=True)

    NEW = 'N'
    ASSEMBLED = 'A'
    SHIPPED = 'S'

    ORDER_STATUS = (
        (NEW, 'Новый'),
        (ASSEMBLED, 'Укомплектован'),
        (SHIPPED, 'Отправлен'),
    )

    status = models.CharField("Статус", max_length=1, choices=ORDER_STATUS, default=NEW)

    class Meta:
        ordering = ('-created', )
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def get_total_cost(self):
        return round(sum(item.get_cost() for item in self.items.all()))

    def __str__(self):
        return 'Order {}'.format(self.id)


class OrderItem(models.Model):
    """ Модель строк заказа """
    order = models.ForeignKey(Order, verbose_name="Заказ", related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name="Товар", related_name='order_item', on_delete=models.CASCADE)
    # price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    quantity = models.DecimalField("Количество", max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Строка заказа'
        verbose_name_plural = 'Строки заказа'

    def get_cost(self):
        # return self.price * self.quantity
        return self.product.price * self.quantity

    def __str__(self):
        return self.product.name


class Container(models.Model):
    """ Модель контейнера """
    order_item = models.ForeignKey(OrderItem, verbose_name="Товар", on_delete=models.CASCADE)
    number = models.CharField("Номер контейнера", max_length=20)
    quantity = models.DecimalField("Количество", max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Контейнер"
        verbose_name_plural = "Контейнеры"

    def __str__(self):
        return self.number
