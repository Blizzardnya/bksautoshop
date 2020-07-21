from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone

from .models import Container, Order


@receiver([post_save, post_delete], sender=Container)
def update_assembled(sender, instance, **kwargs):
    """ Сигнал для обновления статуса и времени заказа """
    order = instance.order_item.order

    if order.is_full_assembled:
        order.status = Order.ASSEMBLED
        order.assembled = timezone.now()
    else:
        order.status = Order.PROCESSED
        order.assembled = None

    order.save(update_fields=['status', 'assembled'])
