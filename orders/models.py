from django.db import models
from accounts.models import ShopUser
from bid.models import Product, Unit


class Order(models.Model):
    """ Модель заказа """
    user = models.ForeignKey(ShopUser, verbose_name="Пользователь", on_delete=models.CASCADE)
    created = models.DateTimeField("Дата создания", auto_now_add=True)
    assembled = models.DateTimeField("Дата комплектовки", null=True, blank=True)
    shipped = models.DateTimeField("Дата отгрузки", null=True, blank=True)

    NEW = 'N'
    PROCESSED = 'P'
    ASSEMBLED = 'A'
    SHIPPED = 'S'

    ORDER_STATUS = (
        (NEW, 'Новый'),
        (PROCESSED, 'Обработан'),
        (ASSEMBLED, 'Укомплектован'),
        (SHIPPED, 'Отправлен'),
    )

    STATUS_COLORS = {
        NEW: 'primary',
        PROCESSED: 'warning',
        ASSEMBLED: 'info',
        SHIPPED: 'success'
    }

    status = models.CharField("Статус", max_length=1, choices=ORDER_STATUS, default=NEW)

    class Meta:
        ordering = ('-created', )
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def get_total_cost(self):
        return round(sum(item.get_cost() for item in self.items.all()), 2)

    def get_items_for_packer(self):
        weight_units = Unit.objects.filter(type=Unit.WEIGHT)
        return self.items.filter(product__unit__in=weight_units)

    def get_status_color(self):
        return self.STATUS_COLORS.get(self.status)

    def __str__(self):
        return 'Order {}'.format(self.id)

    get_total_cost.short_description = 'Итого'


class OrderItem(models.Model):
    """ Модель строк заказа """
    order = models.ForeignKey(Order, verbose_name="Заказ", related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name="Товар", related_name='order_item', on_delete=models.CASCADE)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    quantity = models.DecimalField("Количество", max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Строка заказа'
        verbose_name_plural = 'Строки заказа'

    def get_cost(self):
        return round(self.price * self.quantity, 2)

    def __str__(self):
        return self.product.name

    get_cost.short_description = 'Стоимость'


class Container(models.Model):
    """ Модель контейнера """
    order_item = models.ForeignKey(OrderItem, verbose_name="Товар", related_name='containers', on_delete=models.CASCADE)
    number = models.CharField("Номер контейнера", max_length=20)
    quantity = models.DecimalField("Количество", max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Контейнер"
        verbose_name_plural = "Контейнеры"

    def __str__(self):
        return self.number
