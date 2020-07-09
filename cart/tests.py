from decimal import Decimal

from django.test import TestCase

from bid.models import Category, Unit, Product, ProductMatrix
from .cart import Cart


class CartTestCase(TestCase):
    def setUp(self) -> None:
        # Создание товара
        test_category = Category.objects.create(name='Meat', slug='meat', root_category=None)
        test_unit_1 = Unit.objects.create(name='Kilograms', short_name='kg.', type=Unit.WEIGHT)
        test_unit_2 = Unit.objects.create(name='Piece', short_name='pc.', type=Unit.PIECE)
        test_matrix = ProductMatrix.objects.create(name='Small shop')
        self.test_product_1 = Product.objects.create(barcode='111111111', name='Goat meat', slug='goat-meat',
                                                     unit=test_unit_1, price=3.65, category=test_category,
                                                     storage_condition=Product.COOLED)
        self.test_product_1.matrix.add(test_matrix)

        self.test_product_2 = Product.objects.create(barcode='111111112', name='Koala meat 200g.',
                                                     slug='koala-meat-200g', unit=test_unit_2, price=77.16,
                                                     category=test_category, storage_condition=Product.COOLED)
        self.test_product_2.matrix.add(test_matrix)

        self.cart = Cart(self.client.session)
        self.cart.add(self.test_product_1, 2)

    def test_cart_add(self):
        self.cart.add(self.test_product_2, 3)
        self.assertEqual(len(self.cart), 2)

    def test_cart_remove(self):
        self.cart.remove(self.test_product_1)
        self.assertEqual(len(self.cart), 0)

    def test_get_total_price(self):
        self.assertEqual(self.cart.get_total_price(), round(Decimal(7.30),2))

