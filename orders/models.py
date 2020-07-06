from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.db.models import Count, Q

from accounts.models import ShopUser
from bid.models import Product, Unit

try:
    from bksautoshop.local_settings import BID_TIME
except (ImportError, ModuleNotFoundError):
    from bksautoshop.prod_settings import BID_TIME


class PackerOrderManager(models.Manager):
    def get_queryset(self):
        today = timezone.now()
        date = timezone.datetime(year=today.year, month=today.month, day=today.day,
                                 tzinfo=timezone.get_current_timezone(), **BID_TIME)

        weight_units = Unit.objects.filter(type=Unit.WEIGHT)
        items = Count('items', filter=Q(items__product__unit__in=weight_units, items__packed=False))
        return super().get_queryset().annotate(items_count=items).filter(status=Order.PROCESSED, created__lte=date,
                                                                         items_count__gt=0)


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

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'

    def get_total_cost(self):
        return round(sum(item.get_cost() for item in self.items.all()), 2)

    def get_items_for_packer(self):
        weight_units = Unit.objects.filter(type=Unit.WEIGHT)
        return self.items.filter(product__unit__in=weight_units, packed=False)

    def get_status_color(self):
        return self.STATUS_COLORS.get(self.status)

    def get_absolute_url(self):
        return reverse('orders:view_order', args=[self.id])

    def is_full_assembled(self):
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
        return round(self.price * self.quantity, 2)

    def get_total_quantity_in_containers(self):
        return round(sum(container.quantity for container in self.containers.all()), 2)

    def __str__(self):
        return self.product.name

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

    def __str__(self):
        return self.number
