from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from accounts.forms import LoginForm
from accounts.models import ShopUser
from .forms import SearchForm
from .models import Category
from .services import get_product_list_service, search_products_service, get_user_last_orders_service


def page_not_found_404_view(request, exception):
    """ Страница с ошибкой 404 """
    return render(request, 'bid/404.html', status=404)


def internal_server_error_500_view(request):
    """ Страница с ошибкой 500 """
    return render(request, 'bid/500.html', status=500)


def index(request):
    """ Главная страница приложения """
    last_orders = get_user_last_orders_service(request.user, 3)
    form = LoginForm()
    return render(request, 'bid/index.html', {'last_orders': last_orders, 'form': form})


@login_required()
@permission_required('accounts.is_merchandiser')
def product_list_view(request, category_slug=None):
    """ Просмотр списка товаров """
    category = None
    categories = []
    products_list = []

    try:
        category, categories, products_list = get_product_list_service(request.user, category_slug)
    except ShopUser.DoesNotExist:
        messages.error(request, f'Пользователь магазина для {str(request.user)} не найден')
    except Category.DoesNotExist:
        messages.error(request, f'Категория {category_slug} не найдена')

    paginator = Paginator(products_list, 12)
    page = request.GET.get('page')
    products = paginator.get_page(page)

    context = {
        'category': category,
        'categories': categories,
        'products': products
    }

    return render(request, 'bid/product/list.html', context)


@login_required()
@permission_required('accounts.is_merchandiser')
@require_POST
def prepare_search_view(request):
    """ Получение и обработка ключевого слова для поиска """
    search_query = None

    form = SearchForm(request.POST)
    if form.is_valid():
        search_query = form.cleaned_data['search_input']

    return redirect('bid:search_results', word=search_query)


def search_results_view(request, word):
    """ Поиск товаров по ключевому слову """
    search_products = []

    try:
        search_products = search_products_service(request.user, word)
    except ShopUser.DoesNotExist:
        messages.error(request, f'Пользователь магазина для {str(request.user)} не найден')

    context = {
        'key_word': word,
        'products': search_products
    }

    return render(request, 'bid/search.html', context)
