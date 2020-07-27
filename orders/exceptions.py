class NotPackedException(Exception):
    """ Вызывается если позиция ещё не упакована """

    def __init__(self):
        super().__init__('Данная позиция ещё не упакована')


class NotSortedException(Exception):
    """ Вызывается если заявка ещё полностью не укомплектована """

    def __init__(self):
        super().__init__('Заявка всё ещё не укомплектована')


class ContainerOverflowException(Exception):
    """ Вызывается если количество товара в контейнере больше количества товара по заявке """

    def __init__(self):
        super().__init__('Количество товара в контейнере не может быть больше количества товара по заявке')


class CartIsEmptyException(Exception):
    """ Вызывается если в корзине нет товаров """

    def __init__(self):
        super().__init__('Ваша корзина пуста')


class OrderStatusException(Exception):
    """ Вызывается при ошибке в работе со статусом заявки """

    def __init__(self, message):
        if not message:
            message = 'Ошибка статуса заяки'
        super().__init__(message)


class InvalidOrderStatusException(OrderStatusException):
    """ Вызывается при неизвестном статусе для заказа """

    def __init__(self):
        super().__init__('Неизвестное значение статуса')


class NotNewOrderStatusException(OrderStatusException):
    """ Вызывается если заявка имеет статус отличный от NEW"""

    def __init__(self):
        super().__init__('Изменения статуса у данной заявки запрещено')
