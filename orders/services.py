import logging
from decimal import Decimal

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from django.db.utils import Error

from accounts.models import ShopUser
from .models import Order, OrderItem, Container
from .exceptions import NotPackedException, ContainerOverflowException, NotSortedException
from cart.cart import Cart

logger = logging.getLogger(__name__)


def create_order_service(user: User, cart: Cart) -> Order:
    """
    Создание заявки
    :param user: Пользователь
    :param cart: Корзина
    :return: Заявка
    """
    shop_user = ShopUser.objects.get(user=user)
    try:
        with transaction.atomic():
            order = Order.objects.create(user=shop_user)

            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity'],
                    packed=not item['product'].unit.is_weight_type())

            logger.info(f'Order №{str(order.id)} was created by user {shop_user}')

        cart.clear()
    except Error as err:
        logger.error(f'Order was not created by user {shop_user}, error text: {str(err)}')
        raise

    return order


def update_container_quantity_service(container: Container, quantity: Decimal, increment_quantity: bool) -> None:
    """
    Обновление количества товара в контейнере
    :param container: Контейнер
    :param quantity: Кол-во
    :param increment_quantity: Нужно ли добавлять кол-во к уже имеющемуся
    """
    if increment_quantity:
        container.quantity += quantity
    else:
        container.quantity = quantity
    container.save(update_fields=['quantity'])


def set_container_to_order_item_service(container_number: int, order_item_id: int, quantity: Decimal) -> None:
    """
    Добавление контейнера для строки завки
    :param container_number: Номер контейнера
    :param order_item_id: Идентификатор строки заявки
    :param quantity: Кол-во
    """
    order_item = get_object_or_404(OrderItem, id=order_item_id)

    if not order_item.packed:
        raise NotPackedException

    containers_total_quantity = order_item.get_total_quantity_in_containers()

    if not order_item.quantity >= containers_total_quantity + quantity:
        raise ContainerOverflowException

    container = Container.objects.filter(number=container_number, order_item=order_item).first()

    if not container:
        Container.objects.create(order_item=order_item, number=container_number, quantity=quantity)
    else:
        update_container_quantity_service(container, quantity, True)


def set_container_to_order_service(order_id: int, container_number: int):
    """
    Установка контейнера для всех позиций в заявке
    :param order_id: Идентификатор заявки
    :param container_number: Номер контейнера
    :return: Список позиций уже размещённых в контейнеры, Список не упакованных товаров
    """
    order = get_object_or_404(Order, id=order_id)
    assembled_products = []
    not_packed = []

    for item in order.items.all():
        if item.packed:
            container_total_quantity = item.get_total_quantity_in_containers()

            if container_total_quantity < item.quantity:
                container = Container.objects.filter(number=container_number, order_item=item).first()

                if not container:
                    Container.objects.create(
                        order_item=item,
                        number=container_number,
                        quantity=item.quantity - container_total_quantity)
                else:
                    update_container_quantity_service(container, item.quantity, False)
            else:
                assembled_products.append(item.product.name)
        else:
            not_packed.append(item.product.name)

    return assembled_products, not_packed


def delete_container_service(container_id: int) -> None:
    """
    Удаление контейнера
    :param container_id: Идентификатор контейнера
    """
    container = get_object_or_404(Container, id=container_id)
    container.delete()


def change_order_item_packed_state(order_item: OrderItem, packed_state: bool) -> None:
    """
    Изменение состояния упаковки строки заявки
    :param order_item: Строка заявки
    :param packed_state: Состояние
    """
    order_item.packed = packed_state
    order_item.save(update_fields=['packed'])


def set_order_as_packed_service(order_id: int) -> None:
    """
    Пометить заявку с весовым товаром как упакованную
    :param order_id: Идентификатор заявки
    """
    order = get_object_or_404(Order, id=order_id)

    for item in order.items.filter(packed=False):
        change_order_item_packed_state(item, True)


def set_order_item_as_packed_service(order_item_id: int) -> None:
    """
    Пометить строку заявки с весовым товаром как упакованную
    :param order_item_id: Идентификатор строки завки
    """
    order_item = get_object_or_404(OrderItem, id=order_item_id)
    change_order_item_packed_state(order_item, True)


def changer_order_status_service(order: Order, status: Order.ORDER_STATUS) -> None:
    """
    Изменение статуса заявки
    :param order: Заявка
    :param status: Статус
    """
    order.status = status

    if status == Order.ASSEMBLED:
        order.assembled = timezone.now()
    elif status == Order.SHIPPED:
        order.shipped = timezone.now()

    order.save()


def set_order_as_shipped_service(order_id: int) -> None:
    """
    Пометить заявку как отправленную
    :param order_id: Идентификатор заявки
    """
    order = get_object_or_404(Order, id=order_id)

    if order.status == Order.PROCESSED:
        raise NotSortedException

    if order.status != Order.SHIPPED:
        changer_order_status_service(order, Order.SHIPPED)
        logger.info(f'Order №{str(order.id)} marked as shipped.')
