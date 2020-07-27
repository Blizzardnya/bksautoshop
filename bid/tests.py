from django.contrib.auth.models import User
from django.test import TestCase

from accounts.models import ShopUser
from .models import Product, Category, Unit, ProductMatrix, Shop, Stock
from .services import search_products_service, get_product_list_service, get_categories_by_root_category_service


class BidTestCase(TestCase):
    def setUp(self) -> None:
        test_category_1 = Category.objects.create(name='Meat', slug='meat', root_category=None)
        self.test_category_2 = Category.objects.create(name='Fruits', slug='fruits', root_category=None)
        test_unit_1 = Unit.objects.create(name='Kilograms', short_name='kg.', type=Unit.WEIGHT)
        test_unit_2 = Unit.objects.create(name='Piece', short_name='pc.', type=Unit.PIECE)
        test_matrix = ProductMatrix.objects.create(name='Small shop')
        self.test_product_1 = Product.objects.create(barcode='111111111', name='Goat meat', slug='goat-meat',
                                                     unit=test_unit_1, price=3.65, category=test_category_1,
                                                     storage_condition=Product.COOLED)
        self.test_product_1.matrix.add(test_matrix)

        test_product_2 = Product.objects.create(barcode='111111112', name='Mango 200g.',
                                                slug='mango-200g', unit=test_unit_2, price=77.16,
                                                category=self.test_category_2, storage_condition=Product.COOLED)
        test_product_2.matrix.add(test_matrix)

        # Создание магазина
        test_stock = Stock.objects.create(name='Test stock', stock_type=Stock.ORDINARY)
        test_shop = Shop.objects.create(address='Test address', product_matrix=test_matrix, stock=test_stock)

        # Создание пользователя
        self.test_user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        ShopUser.objects.create(user=self.test_user, phone=None, shop=test_shop)

    def test_get_product_list_service_no_category(self):
        category, categories, products_list = get_product_list_service(self.test_user)
        self.assertIsNone(category)
        self.assertEqual(len(products_list), 2)

    def test_get_product_list_service_category(self):
        category, categories, products_list = get_product_list_service(self.test_user, self.test_category_2.slug)
        self.assertEqual(category, self.test_category_2)
        self.assertEqual(len(categories), 0)
        self.assertEqual(len(products_list), 1)

    def test_search_products_service(self):
        products = search_products_service(self.test_user, 'goat')
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0], self.test_product_1)


class GetCategoriesByRootTestCase(TestCase):
    def setUp(self) -> None:
        test_1 = Category.objects.create(name='test_1', slug='test_1', root_category=None)
        test_1_1 = Category.objects.create(name='test_1_1', slug='test_1_1', root_category=test_1)
        test_1_2 = Category.objects.create(name='test_1_2', slug='test_1_2', root_category=test_1)
        test_1_2_1 = Category.objects.create(name='test_1_2_1', slug='test_1_2_1', root_category=test_1_2)
        test_2 = Category.objects.create(name='test_2', slug='test_2', root_category=None)
        test_2_1 = Category.objects.create(name='test_2_1', slug='test_2_1', root_category=test_2)
        self.test_3 = Category.objects.create(name='test_3', slug='test_3', root_category=None)
        test_3_1 = Category.objects.create(name='test_3_1', slug='test_3_1', root_category=self.test_3)
        test_3_1_1 = Category.objects.create(name='test_3_1_1', slug='test_3_1_1', root_category=test_3_1)
        test_3_1_1_1 = Category.objects.create(name='test_3_1_1_1', slug='test_3_1_1_1', root_category=test_3_1_1)
        test_3_2 = Category.objects.create(name='test_3_2', slug='test_3_2', root_category=self.test_3)

    def test_None_True(self):
        result = get_categories_by_root_category_service(None, True)
        self.assertEqual(len(result), 11)

    def test_None_False(self):
        result = get_categories_by_root_category_service(None, False)
        self.assertEqual(len(result), 3)

    def test_Value_False(self):
        result = get_categories_by_root_category_service(self.test_3, False)
        self.assertEqual(len(result), 2)

    def test_Value_True(self):
        result = get_categories_by_root_category_service(self.test_3, True)
        self.assertEqual(len(result), 4)
