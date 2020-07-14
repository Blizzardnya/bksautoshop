from decimal import Decimal
from typing import Union, Optional

from django.utils import timezone

from .forms import ContainerPieceOrderItemAddForm, ContainerWeightOrderItemAddForm

try:
    from bksautoshop.local_settings import BID_TIME
except (ImportError, ModuleNotFoundError):
    from bksautoshop.prod_settings import BID_TIME


container_form_union = Union[ContainerPieceOrderItemAddForm, ContainerWeightOrderItemAddForm]


def get_today_process_bid_datetime() -> timezone.datetime:
    """
    Получения сегодняшней даты и времени окончания обработки заказов
    :return: Дата и время обработки заказов
    """
    today = timezone.now()
    date = timezone.datetime(year=today.year, month=today.month, day=today.day, tzinfo=None, **BID_TIME)

    return date


def get_container_order_add_form(is_weight_type: bool, number: Optional[int], quantity: Decimal,
                                 disabled_number: bool) -> container_form_union:
    """
    Получение формы для добавления контейнера с предустановленными значениями
    :param is_weight_type: Является ли товар весовым
    :param number: Номер контейнера
    :param quantity: Кол-во
    :param disabled_number: Деавтивировать ли поле с номером
    :return: Форма
    """
    if is_weight_type:
        form = ContainerWeightOrderItemAddForm(
            disabled_number=disabled_number,
            initial={
                'container_number': number,
                'quantity': quantity
            }
        )
    else:
        form = ContainerPieceOrderItemAddForm(
            disabled_number=disabled_number,
            initial={
                'container_number': number,
                'quantity': int(quantity)
            }
        )

    return form
