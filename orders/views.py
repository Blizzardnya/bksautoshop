from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.views import generic

from .models import Order, OrderItem
from cart.cart import Cart
from accounts.models import SystemUser


@login_required()
@permission_required('orders.add_order')
def create_order(request):
    """ Создание заявки """
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


class OrderListView(LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
    """ Просмотр списка заявок пользователя """
    model = Order
    context_object_name = 'orders'
    template_name = 'orders/list.html'
    paginate_by = 12
    permission_required = 'orders.view_order'

    def get_queryset(self):
        return Order.objects.filter(
            user=SystemUser.objects.get(user=self.request.user)
        ).order_by('-created')


class OrderView(LoginRequiredMixin, PermissionRequiredMixin, generic.DetailView):
    """ Просмотр заявки пользователя """
    model = Order
    template_name = 'orders/view.html'
    permission_required = 'orders.view_order'
