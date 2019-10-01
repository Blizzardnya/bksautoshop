from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Order, OrderItem
from cart.cart import Cart
from accounts.models import SystemUser


@login_required()
def create_order(request):
    cart = Cart(request)
    scser = SystemUser.objects.get(user=request.user)
    if request.method == 'POST':
        if len(cart) == 0:
            messages.add_message(request, 40, 'Ваша корзина пуста.')
            return render(request, 'orders/create.html')
        order = Order.objects.create(user=scser)

        for item in cart:
            OrderItem.objects.create(order=order,
                                     product=item['product'],
                                     price=item['price'],
                                     quantity=item['quantity'])
        cart.clear()
        return render(request, 'orders/created.html', context={'order': order})
    else:
        return render(request, 'orders/create.html')
