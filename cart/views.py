from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from bid.models import Product
from .cart import Cart
# from .forms import CartAddProductForm
from .forms import CartAddWeightProductForm, CartAddPieceProductForm
from django.contrib.auth.decorators import login_required, permission_required


@require_POST
@permission_required('orders.add_order')
def cart_add(request, product_id):
    """ Добавление товара в корзину """
    # next_path = request.POST.get('next', '/')
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    if product.unit.is_weight_type:
        form = CartAddWeightProductForm(request.POST)
    else:
        form = CartAddPieceProductForm(request.POST)
    # form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=product, quantity=cd['quantity'], update_quantity=cd['update'])

    # return redirect(next_path)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def cart_remove(request, product_id):
    """ Удаление товара из корзины """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart:cart_detail')


def cart_clear(request):
    """ Очистка корзины """
    cart = Cart(request)
    cart.clear()
    return redirect('cart:cart_detail')


@login_required()
def cart_detail(request):
    """ Просмотр корзины """
    cart = Cart(request)
    for item in cart:
        if item.get('product').unit.is_weight_type():
            item['update_quantity_form'] = CartAddWeightProductForm(initial={'quantity': item['quantity'],
                                                                             'update': True})
        else:
            item['update_quantity_form'] = CartAddPieceProductForm(initial={'quantity': item['quantity'],
                                                                            'update': True})
        # item['update_quantity_form'] = CartAddProductForm(initial={'quantity': item['quantity'], 'update': True})
    return render(request, 'cart/detail.html', {'cart': cart})
