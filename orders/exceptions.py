class NotPackedException(Exception):
    def __init__(self):
        super().__init__('Данная позиция ещё не упакована')


class ContainerOverflowException(Exception):
    def __init__(self):
        super().__init__('Количество товара в контейнере не может быть больше количества товара по заявке')
