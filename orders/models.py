from django.db import models
from django.urls import reverse
from django.db.models import Count, Q

from accounts.models import ShopUser
from bid.models import Product, Unit
from .utils import get_today_process_bid_datetime


class PackerOrderManager(models.Manager):
    """ Выборка заявок для упаковщика """

    def get_queryset(self):
        date = get_today_process_bid_datetime()

        weight_units = Unit.objects.filter(type=Unit.WEIGHT)
        items = Count('items', filter=Q(items__product__unit__in=weight_units, items__packed=False))
        return super().get_queryset().annotate(items_count=items).filter(status=Order.PROCESSED, created__lte=date,
                                                                         items_count__gt=0)


class SorterOrderManager(models.Manager):
    """ Выборка заявок для сортировщика """

    def get_queryset(self):
        date = get_today_process_bid_datetime()

        return super().get_queryset().filter(
            status__in=(Order.PROCESSED, Order.ASSEMBLED), created__lte=date
        )


class Order(models.Model):
    """ Модель заявки """
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
    objects = models.Manager()
    orders_for_packer = PackerOrderManager()
    orders_for_sorter = SorterOrderManager()

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'

    def get_total_cost(self):
        return round(sum(item.get_cost() for item in self.items.all()), 2)

    def get_items_for_packer(self):
        """ Получение только весового неупаковонного товара для упаковщика """
        weight_units = Unit.objects.filter(type=Unit.WEIGHT)
        return self.items.filter(product__unit__in=weight_units, packed=False)

    def get_status_color(self):
        return self.STATUS_COLORS.get(self.status)

    def get_absolute_url(self):
        return reverse('orders:view_order', args=[self.id])

    @property
    def is_full_assembled(self):
        """ Проверка упакован ли весь товар в контейнеры """
        total_items_quantity = 0
        total_containers_quantity = 0

        for item in self.items.all():
            total_items_quantity += item.quantity
            total_containers_quantity += item.get_total_quantity_in_containers()

        return total_items_quantity == total_containers_quantity

    def __str__(self):
        return f'Заявка №{self.id}'

    get_total_cost.short_description = 'Итого'


class OrderItem(models.Model):
    """ Модель строк заявки """
    order = models.ForeignKey(Order, verbose_name="Заявка", related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name="Товар", related_name='order_item', on_delete=models.CASCADE)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    quantity = models.DecimalField("Количество", max_digits=10, decimal_places=2)
    packed = models.BooleanField("Упаковано", default=True)

    class Meta:
        verbose_name = 'Строка заявки'
        verbose_name_plural = 'Строки заявки'

    def get_cost(self):
        """ Стоимость """
        return round(self.price * self.quantity, 2)

    def get_total_quantity_in_containers(self):
        """ Количество товара в контейнерах """
        return round(sum(container.quantity for container in self.containers.all()), 2)

    @property
    def missing_quantity_in_containers(self):
        missing_quantity = self.quantity - self.get_total_quantity_in_containers()
        return missing_quantity if self.product.unit.is_weight_type else int(missing_quantity)

    def __str__(self):
        return self.product.name

    @property
    def packed_to_str(self):
        return 'Да' if self.packed else 'Нет'

    get_cost.short_description = 'Стоимость'


class Container(models.Model):
    """ Модель контейнера """
    order_item = models.ForeignKey(OrderItem, verbose_name="Товар", related_name='containers', on_delete=models.CASCADE)
    number = models.CharField("Номер контейнера", max_length=20)
    quantity = models.DecimalField("Количество", max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Контейнер"
        verbose_name_plural = "Контейнеры"

    @property
    def quantity_by_weight_type(self):
        return self.quantity if self.order_item.product.unit.is_weight_type else int(self.quantity)

    def __str__(self):
        return self.number
