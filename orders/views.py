from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import generic

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


class OrderListView(LoginRequiredMixin, generic.ListView):
    model = Order
    context_object_name = 'orders'
    template_name = 'orders/list.html'
    paginate_by = 12

    def get_queryset(self):
        """ Все заказы оформленные пользователем """
        return Order.objects.filter(
            user=SystemUser.objects.get(user=self.request.user)
        ).order_by('-created')


class OrderView(generic.DetailView):
    model = Order
    template_name = 'orders/view.html'
