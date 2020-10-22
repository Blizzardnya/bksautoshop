import logging
from typing import List

from django.contrib.auth.models import User
from django.contrib.postgres.search import SearchVector
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from accounts.models import ShopUser
from orders.models import Order
from .models import Category, Product

logger = logging.getLogger(__name__)


def get_product_list_service(user: User, category_slug: str = None):
    """
    Получени товаров на основании категории
    :param user: Пользователь
    :param category_slug: Категория
    :return: Головная категория, дочерние категории, товары
    """
    try:
        shop_user = ShopUser.objects.get(user=user)

        if category_slug:
            category = Category.objects.get(slug=category_slug)
            categories = Category.objects.filter(root_category=category)
            products_list = Product.objects.filter(
                Q(category=category) | Q(category__in=categories),
                matrix=shop_user.shop.product_matrix
            )
        else:
            category = None
            categories = Category.objects.filter(root_category=None)
            products_list = Product.objects.filter(matrix=shop_user.shop.product_matrix)
    except ShopUser.DoesNotExist:
        logger.error(f'Пользователь магазина для {str(user)} не найден')
        raise
    except Category.DoesNotExist:
        logger.error(f'Категория {category_slug} не найдена')
        raise

    return category, categories, products_list


def search_products_service(user: User, word: str):
    """
    Поисе товаров по заданному ключевому слову
    :param user: Пользователь
    :param word: Клчевое слово
    :return: Товары
    """
    try:
        shop_user = ShopUser.objects.get(user=user)
        search_products = Product.objects.annotate(search=SearchVector('barcode', 'name'))\
                                         .filter(search=word, matrix=shop_user.shop.product_matrix)
    except ShopUser.DoesNotExist:
        logger.error(f'Пользователь магазина для {str(user)} не найден')
        raise

    return search_products


def get_user_last_orders_service(user: User, count: int):
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


def get_categories_by_root_category_service(root_category: Category = None, get_nested: bool = False) -> List[Category]:
    """
    Получение катергорий товаров по родительской категории
    :param root_category: Роительская категория
    :param get_nested: Признак получения всех категорий
    :return: Категории
    """
    result = []

    if get_nested:
        if root_category:
            categories = Category.objects.filter(root_category=root_category)
            result.extend(categories)
            for category in categories:
                result.extend(get_categories_by_root_category_service(category, True))
        else:
            result = Category.objects.all()
    else:
        result = Category.objects.filter(root_category=root_category)

    return result
