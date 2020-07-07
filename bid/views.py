from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.http import require_POST

from cart.forms import CartAddWeightProductForm, CartAddPieceProductForm
from .forms import SearchForm
from .services import get_product_list_service, search_products_service, get_user_last_orders


def index(request):
    """ Главная страница приложения """
    last_orders = get_user_last_orders(request.user, 3)
    return render(request, 'bid/index.html', {'last_orders': last_orders})


@login_required()
@permission_required('accounts.is_merchandiser')
def product_list(request, category_slug=None):
    """ Просмотр списка товаров """
    category, categories, products_list = get_product_list_service(request.user, category_slug)

    paginator = Paginator(products_list, 12)
    page = request.GET.get('page')
    products = paginator.get_page(page)

    context = {
        'category': category,
        'categories': categories,
        'products': products,
        'cart_weight_product_form': CartAddWeightProductForm(),
        'cart_piece_product_form': CartAddPieceProductForm(),
    }

    return render(request, 'bid/product/list.html', context)


@login_required()
@permission_required('accounts.is_merchandiser')
@require_POST
def prepare_search(request):
    """ Получение и обработка ключевого слова для поиска """
    search_products = None

    form = SearchForm(request.POST)
    if form.is_valid():
        search_products = form.cleaned_data['search_input']

    return redirect('bid:search_results', word=search_products)


def search_results(request, word):
    """ Поиск товаров по ключевому слову"""
    search_products = search_products_service(request.user, word)

    context = {
        'key_word': word,
        'products': search_products,
        'cart_weight_product_form': CartAddWeightProductForm(),
        'cart_piece_product_form': CartAddPieceProductForm(),
    }

    return render(request, 'bid/search.html', context)
