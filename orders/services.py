import logging
from decimal import Decimal
from typing import List, Union

from django.contrib.auth.models import User
from django.db import transaction
from django.db.utils import Error
from django.utils import timezone

from accounts.models import ShopUser
from cart.cart import Cart
from .exceptions import NotPackedException, ContainerOverflowException, NotSortedException, CartIsEmptyException
from .models import Order, OrderItem, Container

logger = logging.getLogger(__name__)


def create_order_service(user: User, cart: Cart) -> Order:
    """
    Создание заявки
    :param user: Пользователь
    :param cart: Корзина
    :return: Заявка
    """
    try:
        shop_user = ShopUser.objects.get(user=user)
    except ShopUser.DoesNotExist:
        logger.error(f'Пользователь магазина для {str(user)} не найден')
        raise

    if len(cart) == 0:
        raise CartIsEmptyException

    try:
        with transaction.atomic():
            order = Order.objects.create(user=shop_user)

            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity'],
                    packed=not item['product'].unit.is_weight_type)

        logger.info(f'{str(order)} была создана пользователем {shop_user}')
        cart.clear()
    except Error as err:
        logger.error(f'Заявка пользователя {shop_user} не создана, текст ошибки: {str(err)}')
        raise

    return order


def _update_container_quantity_service(container: Container, quantity: Union[Decimal, int],
                                       increment_quantity: bool) -> None:
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


def update_order_item_container_service(container_id: int, quantity: Union[Decimal, int]) -> None:
    """
    Обновление кол-ва товара в контейнере для строки заявки
    :param container_id: Идентификатор контейнера
    :param quantity: Кол-во
    """
    try:
        container = Container.objects.get(id=container_id)
        order_item = container.order_item

        if container.quantity != quantity:
            # Проверка на переполнение
            # Кол-во недостающего товара + Предыдущее кол-во >= Новое кол-во
            if order_item.missing_quantity_in_containers + container.quantity >= quantity:
                _update_container_quantity_service(container, quantity, False)
            else:
                raise ContainerOverflowException
    except Container.DoesNotExist:
        logger.error(f'Контейнер с идентификатором {str(container_id)} не найден')
        raise


def set_container_to_order_item_service(container_number: int, order_item_id: int,
                                        quantity: Union[Decimal, int]) -> None:
    """
    Добавление контейнера для строки завки
    :param container_number: Номер контейнера
    :param order_item_id: Идентификатор строки заявки
    :param quantity: Кол-во
    """
    try:
        order_item = OrderItem.objects.get(id=order_item_id)

        if not order_item.packed:
            raise NotPackedException

        if order_item.missing_quantity_in_containers < quantity:
            raise ContainerOverflowException

        container, created = Container.objects.get_or_create(order_item=order_item, number=container_number,
                                                             defaults={'quantity': quantity})

        if not created:
            _update_container_quantity_service(container, quantity, True)
    except OrderItem.DoesNotExist:
        logger.error(f'В заявке нет строки с идентификатором {str(order_item_id)}')
        raise


def set_container_to_order_service(order_id: int, container_number: int) -> List[str]:
    """
    Установка контейнера для всех позиций в заявке
    :param order_id: Идентификатор заявки
    :param container_number: Номер контейнера
    :return: Список не упакованных товаров
    """
    try:
        order = Order.objects.get(id=order_id)
        not_packed = []

        for item in order.items.all():
            if item.packed:
                missing_quantity = item.missing_quantity_in_containers

                if missing_quantity != 0:
                    container, created = Container.objects.get_or_create(
                        order_item=item, number=container_number,
                        defaults={'quantity': missing_quantity}
                    )

                    if not created:
                        _update_container_quantity_service(container, missing_quantity, True)
            else:
                not_packed.append(item.product.name)
    except Order.DoesNotExist:
        logger.error(f'Заявки с идентификатором {str(order_id)} не существует')
        raise

    return not_packed


def delete_container_service(container_id: int) -> None:
    """
    Удаление контейнера
    :param container_id: Идентификатор контейнера
    """
    try:
        container = Container.objects.get(id=container_id)
        container.delete()
    except Container.DoesNotExist:
        logger.error(f'Контейнера с идентификатором {str(container_id)} не существует')
        raise


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
    try:
        order = Order.objects.get(id=order_id)

        for item in order.items.filter(packed=False):
            change_order_item_packed_state(item, True)
    except Order.DoesNotExist:
        logger.error(f'Заявки с идентификатором {str(order_id)} не существует')
        raise


def set_order_item_as_packed_service(order_item_id: int) -> None:
    """
    Пометить строку заявки с весовым товаром как упакованную
    :param order_item_id: Идентификатор строки завки
    """
    try:
        order_item = OrderItem.objects.get(id=order_item_id)
        change_order_item_packed_state(order_item, True)
    except OrderItem.DoesNotExist:
        logger.error(f'В заявке нет строки с идентификатором {str(order_item_id)}')
        raise


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
    try:
        order = Order.objects.get(id=order_id)

        if order.status == Order.PROCESSED:
            raise NotSortedException

        if order.status != Order.SHIPPED:
            changer_order_status_service(order, Order.SHIPPED)
            logger.info(f'{str(order)} отмечана как отправленная.')
    except Order.DoesNotExist:
        logger.error(f'Заявки с идентификатором {str(order_id)} не существует')
        raise


def get_orders_by_shop_user_service(user: User) -> List:
    """
    Получение списка заявок для пользователя магазина
    :param user: Пользователь
    :return: Заявки
    """
    try:
        return Order.objects.filter(
            user=ShopUser.objects.get(user=user)
        ).order_by('-created')
    except ShopUser.DoesNotExist:
        logger.error(f'Пользователь магазина для {str(user)} не найден')
        raise
