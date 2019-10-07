from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.contrib.postgres.search import SearchVector

from .models import Category, Product
from orders.models import Order
from accounts.models import ShopUser
from .forms import SearchForm
from cart.forms import CartAddProductForm


def index(request):
    """ Главная страница приложения """
    last_order = None
    if request.user.is_authenticated:
        try:
            last_order = Order.objects.filter(user=ShopUser.objects.get(user=request.user)).order_by('-created')[0]
        except IndexError:
            pass

    return render(request, 'bid/index.html', {'last_order': last_order})


@login_required()
def product_list(request, category_slug=None):
    """ Просмотр списка товаров """
    sys_user = ShopUser.objects.get(user=request.user)
    category = None
    categories = Category.objects.filter(root_category=None)
    products_list = Product.objects.filter(matrix=sys_user.shop.product_matrix)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        categories = Category.objects.filter(root_category=category)
        products_list = Product.objects.filter(
            Q(category=category) | Q(category__in=categories),
            matrix=sys_user.shop.product_matrix
        )

    paginator = Paginator(products_list, 12)
    page = request.GET.get('page')
    products = paginator.get_page(page)

    context = {
        'category': category,
        'categories': categories,
        'products': products,
        'cart_product_form': CartAddProductForm()
    }

    return render(request, 'bid/product/list.html', context)


@login_required()
@require_POST
def prepare_search(request):
    """ Получение и обработка клшючевого слова для поиска """
    # search_products = request.session.get('products', None)
    search_products = None

    form = SearchForm(request.POST)
    if form.is_valid():
        # search_products = Product.objects.annotate(search=SearchVector('barcode', 'name')).filter(
        #     search=form.cleaned_data['search_input'])
        search_products = form.cleaned_data['search_input']

    # context = {
    #     'products': search_products,
    #     'cart_product_form': CartAddProductForm()
    # }
    #
    # return render(request, 'bid/search.html', context)
    return redirect('bid:search_results', word=search_products)


def search_results(request, word):
    """ Поиск товаров по ключевому слову"""
    search_products = Product.objects.annotate(search=SearchVector('barcode', 'name')).filter(search=word)

    context = {
        'key_word': word,
        'products': search_products,
        'cart_product_form': CartAddProductForm()
    }

    return render(request, 'bid/search.html', context)
