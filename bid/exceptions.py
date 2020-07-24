class ProductAlreadyExistException(Exception):
    """ Вызывается если товар уже существует """

    def __init__(self):
        super().__init__('Товар с таким штрих-кодом уже существует')
