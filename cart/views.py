from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from bid.models import Product
from .cart import Cart
from .forms import CartAddProductForm


@require_POST
@permission_required('orders.add_order')
def cart_add_view(request, product_id: int):
    """ Добавление товара в корзину """
    cart = Cart(request.session)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST, is_weight_type=product.unit.is_weight_type)

    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=product, quantity=cd['quantity'], update_quantity=cd['update'])

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def cart_remove_view(request, product_id: int):
    """ Удаление товара из корзины """
    cart = Cart(request.session)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart:cart_detail')


def clear_cart_view(request):
    """ Очистка корзины """
    cart = Cart(request.session)
    cart.clear()
    return redirect('cart:cart_detail')


@login_required()
def cart_detail_view(request):
    """ Просмотр корзины """
    cart = Cart(request.session)
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(
            initial={'quantity': item['quantity'], 'update': True},
            is_weight_type=item.get('product').unit.is_weight_type
        )
    return render(request, 'cart/detail.html', {'cart': cart})
