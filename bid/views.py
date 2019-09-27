from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator

from .models import Category, Product
from cart.forms import CartAddProductForm

# Create your views here.


def index(request):
    return render(request, 'bid/index.html')


def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.filter(root_category=None)
    products_list = Product.objects.all()

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        categories = Category.objects.filter(root_category=category)
        products_list = Product.objects.filter(
            category=category
        )

    paginator = Paginator(products_list, 9)
    page = request.GET.get('page')
    products = paginator.get_page(page)

    context = {
        'category': category,
        'categories': categories,
        'products': products,
        'cart_product_form': CartAddProductForm()
    }

    return render(request, 'bid/product/list.html', context)
