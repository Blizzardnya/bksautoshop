from decimal import Decimal

from django.conf import settings

from bid.models import Product


class Cart:
    def __init__(self, session):
        self.session = session
        cart = self.session.get(settings.CART_SESSION_ID)

        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product: Product, quantity: int = 1, update_quantity: bool = False):
        """Метод добавления товара в корзину

        :param product: Товар
        :param quantity: Количество
        :param update_quantity: Признак обновления
        """
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': str(Decimal(0.0)), 'price': str(product.price)}
        if update_quantity:
            self.cart[product_id]['quantity'] = str(quantity)
        else:
            self.cart[product_id]['quantity'] = str(Decimal(self.cart[product_id]['quantity']) + Decimal(quantity))
        self.save()

    def save(self):
        """ Метод сохранения корзины в сессии """
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True

    def remove(self, product: Product):
        """Метод удаление товара из корзины

        :param product: Товар
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        for product in products:
            self.cart[str(product.id)]['product'] = product

        for item in self.cart.values():
            item['price'] = Decimal(item['price'])
            item['quantity'] = Decimal(item['quantity'])
            item['total_price'] = round(item['price'] * item['quantity'], 2)
            yield item

    def __len__(self):
        """ Количество товаров в корзине """
        return len(self.cart.values())

    def get_total_price(self):
        """ Метод рассчёта итого по корзине """
        return round(sum(Decimal(item['price']) * Decimal(item['quantity']) for item in self.cart.values()), 2)

    def clear(self):
        """ Метод удаления корзины из сессии """
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True
