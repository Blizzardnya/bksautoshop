from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.postgres.search import SearchVector
from django.core.exceptions import ObjectDoesNotExist

from .models import Category, Product
from accounts.models import ShopUser
from orders.models import Order


def get_product_list_service(user: User, category_slug: str):
    """
    Получени товаров на основании категории
    :param user: Пользователь
    :param category_slug: Категория
    :return: Головная категория, дочерние категории, товары
    """
    shop_user = ShopUser.objects.get(user=user)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        categories = Category.objects.filter(root_category=category)
        products_list = Product.objects.filter(
            Q(category=category) | Q(category__in=categories),
            matrix=shop_user.shop.product_matrix
        )
    else:
        category = None
        categories = Category.objects.filter(root_category=None)
        products_list = Product.objects.filter(matrix=shop_user.shop.product_matrix)

    return category, categories, products_list


def search_products_service(user: User, word: str):
    """
    Поисе товаров по заданному ключевому слову
    :param user: Пользователь
    :param word: Клчевое слово
    :return: Товары
    """
    shop_user = ShopUser.objects.get(user=user)
    search_products = Product.objects.annotate(search=SearchVector('barcode', 'name'))\
                                     .filter(search=word, matrix=shop_user.shop.product_matrix)

    return search_products


def get_user_last_orders(user: User, count: int):
    """
    Получить последние заявки пользователя
    :param user: Пользователь
    :param count: Кол-во
    :return: Заявки
    """
    last_orders = []

    if user.is_authenticated:
        try:
            last_orders = Order.objects.filter(user=ShopUser.objects.get(user=user)).order_by('-created')[:count]
        except (IndexError, ObjectDoesNotExist):
            pass

    return last_orders
