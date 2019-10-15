try:
    from bksautoshop.local_settings import BID_TIME
except (ImportError, ModuleNotFoundError):
    from bksautoshop.prod_settings import BID_TIME

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.views import generic
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Count, Q

from .models import Order, OrderItem
from cart.cart import Cart
from accounts.models import ShopUser
from bid.models import Unit


@login_required()
@permission_required('orders.add_order')
def create_order(request):
    """ Создание заявки """
    cart = Cart(request)
    shop_user = ShopUser.objects.get(user=request.user)
    if request.method == 'POST':
        if len(cart) == 0:
            messages.add_message(request, 40, 'Ваша корзина пуста.')
            return render(request, 'orders/merchandiser/create.html')
        order = Order.objects.create(user=shop_user)

        for item in cart:
            OrderItem.objects.create(order=order,
                                     product=item['product'],
                                     price=item['price'],
                                     quantity=item['quantity'])
        cart.clear()
        return render(request, 'orders/merchandiser/created.html', context={'order': order})
    else:
        return render(request, 'orders/merchandiser/create.html')


class OrderListView(LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
    """ Просмотр списка заявок пользователя """
    model = Order
    context_object_name = 'orders'
    template_name = 'orders/merchandiser/list.html'
    paginate_by = 12
    permission_required = 'accounts.is_merchandiser'

    def get_queryset(self):
        return Order.objects.filter(
            user=ShopUser.objects.get(user=self.request.user)
        ).order_by('-created')


class OrderView(LoginRequiredMixin, PermissionRequiredMixin, generic.DetailView):
    """ Просмотр заявки пользователя """
    model = Order
    template_name = 'orders/merchandiser/view.html'
    permission_required = 'orders.view_order'


@login_required()
@permission_required('accounts.is_packer')
def packer_product_list(request):
    today = timezone.now()
    date = timezone.datetime(today.year, today.month, today.day, BID_TIME.get('hour'), BID_TIME.get('minute'),
                             BID_TIME.get('second'), BID_TIME.get('millisecond'), timezone.get_current_timezone())

    weight_units = Unit.objects.filter(type=Unit.WEIGHT)
    items = Count('items', filter=Q(items__product__unit__in=weight_units))
    orders_list = Order.objects.annotate(items_count=items).filter(status=Order.PROCESSED, created__lte=date,
                                                                   items_count__gt=0)

    paginator = Paginator(orders_list, 12)
    page = request.GET.get('page')
    orders = paginator.get_page(page)

    return render(request, 'orders/packer/list.html', {'orders': orders})
