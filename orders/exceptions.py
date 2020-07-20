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
