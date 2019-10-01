from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.postgres.search import SearchVector

from .models import Category, Product
from accounts.models import SystemUser
from .forms import SearchForm
from cart.forms import CartAddProductForm


def index(request):
    return render(request, 'bid/index.html')


@login_required()
def product_list(request, category_slug=None):
    sys_user = SystemUser.objects.get(user=request.user)
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
def search_results(request):
    search_products = None
    form = SearchForm(request.POST)
    if form.is_valid():
        search_products = Product.objects.annotate(search=SearchVector('barcode', 'name')).filter(
            search=form.cleaned_data['search_input'])

    context = {
        'products': search_products,
        'cart_product_form': CartAddProductForm()
    }

    return render(request, 'bid/search.html', context)
