from django.utils import timezone

try:
    from bksautoshop.local_settings import BID_TIME
except (ImportError, ModuleNotFoundError):
    from bksautoshop.prod_settings import BID_TIME


def get_today_process_bid_datetime() -> timezone.datetime:
    """
    Получения сегодняшней даты и времени окончания обработки заказов
    :return: Дата и время обработки заказов
    """
    today = timezone.now()
    date = timezone.datetime(year=today.year, month=today.month, day=today.day, tzinfo=None, **BID_TIME)

    return date
