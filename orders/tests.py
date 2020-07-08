from django.test import TestCase
from django.contrib.auth.models import User

from accounts.models import ShopUser
from bid.models import Product, Category, Unit, ProductMatrix
from .models import Order, OrderItem, Container
from .services import (set_order_as_shipped_service, set_order_as_packed_service, set_order_item_as_packed_service,
                       set_container_to_order_item_service)
from .exceptions import NotPackedException

# Create your tests here.


class OrderTestCase(TestCase):
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

        # Создание пользователя
        test_user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        test_shop_user = ShopUser.objects.create(user=test_user, phone=None)

        # Создание заявки
        self.test_order_1 = Order.objects.create(user=test_shop_user)
        self.test_order_item_1 = OrderItem.objects.create(order=self.test_order_1, product=self.test_product_1,
                                                          price=self.test_product_1.price, quantity=1.82, packed=False)
        self.test_order_item_2 = OrderItem.objects.create(order=self.test_order_1, product=self.test_product_2,
                                                          price=self.test_product_2.price, quantity=2, packed=True)

        self.test_order_id = self.test_order_1.id

    def test_set_order_as_packed_service(self):
        set_order_as_packed_service(self.test_order_id)
        self.test_order_1.refresh_from_db()

        for item in self.test_order_1.items.all():
            self.assertTrue(item.packed)

    def test_set_order_item_as_packed_service(self):
        set_order_item_as_packed_service(self.test_order_item_1.id)
        self.test_order_item_1.refresh_from_db()
        self.assertTrue(self.test_order_item_1.packed)

    def test_set_order_as_shipped_service(self):
        set_order_as_shipped_service(self.test_order_id)
        self.test_order_1.refresh_from_db()
        self.assertEqual(self.test_order_1.status, Order.SHIPPED)

    def test_set_container_to_order_item_service_not_packed(self):
        self.assertRaises(NotPackedException, set_container_to_order_item_service,
                          1, self.test_order_item_1.id, self.test_order_item_1.quantity)

    def test_set_container_to_order_item_service_packed(self):
        set_container_to_order_item_service(2, self.test_order_item_2.id, self.test_order_item_2.quantity)
        container = Container.objects.get(order_item=self.test_order_item_2)
        self.assertIsNotNone(container)
