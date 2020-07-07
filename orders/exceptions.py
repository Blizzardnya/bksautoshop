class NotPackedException(Exception):
    def __init__(self):
        super().__init__('Данная позиция ещё не упакована')


class NotSortedException(Exception):
    def __init__(self):
        super().__init__('Заявка всё ещё не укомплектована')


class ContainerOverflowException(Exception):
    def __init__(self):
        super().__init__('Количество товара в контейнере не может быть больше количества товара по заявке')
