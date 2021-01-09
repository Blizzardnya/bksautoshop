import itertools
import logging
from typing import List

from django.contrib.auth.models import User
from django.db import transaction, Error
from django.utils import timezone

from cart.cart import Cart
from orders.exceptions import NotSortedException, CartIsEmptyException, InvalidOrderStatusException
from orders.models import ShopUser, Order, OrderItem

logger = logging.getLogger(__name__)


def get_orders_by_shop_user_service(user: User) -> List:
    """Получение списка заявок для пользователя магазина

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


def get_orders_by_status(status: str) -> List[Order]:
    """Получения заявок по статусу

    :param status: Статус
    :return: Список зявок
    """
    if not status:
        raise KeyError('Статус не задан')

    if not (status in itertools.chain(*Order.ORDER_STATUS)):
        raise InvalidOrderStatusException

    return Order.objects.filter(status=status)


def set_order_as_shipped_service(order_id: int) -> None:
    """Пометить заявку как отправленную

    :param order_id: Идентификатор заявки
    """
    try:
        order = Order.objects.get(id=order_id)

        if order.status == Order.PROCESSED:
            raise NotSortedException

        if order.status != Order.SHIPPED:
            _changer_order_status_service(order, Order.SHIPPED)
            logger.info(f'{str(order)} отмечана как отправленная.')
    except Order.DoesNotExist:
        logger.error(f'Заявки с идентификатором {str(order_id)} не существует')
        raise


def _changer_order_status_service(order: Order, status: Order.ORDER_STATUS) -> None:
    """Изменение статуса заявки

    :param order: Заявка
    :param status: Статус
    """
    order.status = status

    if status == Order.ASSEMBLED:
        order.assembled = timezone.now()
    elif status == Order.SHIPPED:
        order.shipped = timezone.now()

    order.save()


def set_order_item_as_packed_service(order_item_id: int) -> None:
    """Пометить строку заявки с весовым товаром как упакованную

    :param order_item_id: Идентификатор строки завки
    """
    try:
        order_item = OrderItem.objects.get(id=order_item_id)
        _change_order_item_packed_state(order_item, True)
    except OrderItem.DoesNotExist:
        logger.error(f'В заявке нет строки с идентификатором {str(order_item_id)}')
        raise


def set_order_as_packed_service(order_id: int) -> None:
    """Пометить заявку с весовым товаром как упакованную

    :param order_id: Идентификатор заявки
    """
    try:
        order = Order.objects.get(id=order_id)

        for item in order.items.filter(packed=False):
            _change_order_item_packed_state(item, True)
    except Order.DoesNotExist:
        logger.error(f'Заявки с идентификатором {str(order_id)} не существует')
        raise


def _change_order_item_packed_state(order_item: OrderItem, packed_state: bool) -> None:
    """Изменение состояния упаковки строки заявки

    :param order_item: Строка заявки
    :param packed_state: Состояние
    """
    order_item.packed = packed_state
    order_item.save(update_fields=['packed'])


def create_order_service(user: User, cart: Cart) -> Order:
    """Создание заявки

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
