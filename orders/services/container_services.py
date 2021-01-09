import logging
from decimal import Decimal
from typing import List, Union, Tuple

from orders.exceptions import NotPackedException, ContainerOverflowException
from orders.forms import AddContainerToOrderItemForm
from orders.models import Order, OrderItem, Container

logger = logging.getLogger(__name__)


def get_order_item_and_containers_with_form(order_item_id: int) -> Tuple[OrderItem, List]:
    """ Получение строки завки и её контейнеров с формами обновления, в которых преодпределена информаця

    :param order_item_id: Идентификатор строки заявки
    :return: Строка заявки, Список контейнеров с формами
    """
    try:
        order_item = OrderItem.objects.get(id=order_item_id)
        containers = [{'container': container,
                       'form': AddContainerToOrderItemForm(
                           initial={
                               'container_number': container.number,
                               'quantity': container.quantity_by_weight_type
                           },
                           disabled_number=True,
                           is_weight_type=order_item.product.unit.is_weight_type
                       )
                       } for container in order_item.containers.all()]
        return order_item, containers
    except OrderItem.DoesNotExist:
        logger.error(f'В заявке нет строки с идентификатором {str(order_item_id)}')
        raise


def _update_container_quantity_service(container: Container, quantity: Union[Decimal, int],
                                       increment_quantity: bool) -> None:
    """Обновление количества товара в контейнере

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
    """Обновление кол-ва товара в контейнере для строки заявки

    :param container_id: Идентификатор контейнера
    :param quantity: Кол-во
    """
    try:
        container = Container.objects.get(id=container_id)

        if container.quantity != quantity:
            # Проверка на переполнение
            # Кол-во недостающего товара + Предыдущее кол-во >= Новое кол-во
            if container.order_item.missing_quantity_in_containers + container.quantity >= quantity:
                _update_container_quantity_service(container, quantity, False)
            else:
                raise ContainerOverflowException
    except Container.DoesNotExist:
        logger.error(f'Контейнер с идентификатором {str(container_id)} не найден')
        raise


def set_container_to_order_item_service(container_number: int, order_item_id: int,
                                        quantity: Union[Decimal, int]) -> None:
    """Добавление контейнера для строки завки

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
    """Установка контейнера для всех позиций в заявке

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
    """Удаление контейнера

    :param container_id: Идентификатор контейнера
    """
    try:
        container = Container.objects.get(id=container_id)
        container.delete()
    except Container.DoesNotExist:
        logger.error(f'Контейнера с идентификатором {str(container_id)} не существует')
        raise
