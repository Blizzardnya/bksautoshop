try:
    from bksautoshop.local_settings import BID_TIME
except (ImportError, ModuleNotFoundError):
    from bksautoshop.prod_settings import BID_TIME

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.views import generic
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import Order, OrderItem, Container
from cart.cart import Cart
from accounts.models import ShopUser
from bid.models import Unit
from .forms import ContainerAddForm


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
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                price=item['price'],
                quantity=item['quantity'])
        cart.clear()
        return render(request, 'orders/merchandiser/created.html', context={'order': order})
    else:
        return render(request, 'orders/merchandiser/create.html')


class MerchandiserOrderListView(LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['container_form'] = ContainerAddForm()
        return context


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


class SorterOrderListView(LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
    """ Просмотр списка заявок пользователя """
    model = Order
    context_object_name = 'orders'
    template_name = 'orders/sorter/list.html'
    paginate_by = 12
    permission_required = 'accounts.is_sorter'

    def get_queryset(self):
        today = timezone.now()
        date = timezone.datetime(today.year, today.month, today.day, BID_TIME.get('hour'), BID_TIME.get('minute'),
                                 BID_TIME.get('second'), BID_TIME.get('millisecond'), timezone.get_current_timezone())

        return Order.objects.filter(
            status=Order.PROCESSED, created__lte=date
        ).order_by('-created')


@login_required()
@require_POST
@permission_required('accounts.is_sorter')
def ser_order_container(request, pk):
    order = get_object_or_404(Order, id=pk)
    conainer_number = None
    container_form = ContainerAddForm(request.POST)

    if container_form.is_valid():
        conainer_number = container_form.cleaned_data['container_number']

    if conainer_number:
        for item in order.items.all():
            Container.objects.create(
                order_item=item,
                number=conainer_number,
                quantity=item.quantity)

        order.status = Order.ASSEMBLED
        order.shipped = timezone.now()

        return HttpResponseRedirect(reverse('orders:view_order', args=[pk]))

    messages.add_message(request, 40, 'Контейнер не указан')
    return HttpResponseRedirect(reverse('orders:view_order', args=[pk]))


@login_required()
@permission_required('accounts.is_sorter')
def set_order_as_shipped(request, pk):
    order = get_object_or_404(Order, id=pk)

    if order.status == Order.PROCESSED:
        messages.add_message(request, 40, 'Заявка всё ещё не укомплектована')
        return HttpResponseRedirect(reverse('orders:view_order', args=[pk]))

    order.status = Order.SHIPPED
    order.shipped = timezone.now()
    order.save()
    return HttpResponseRedirect(reverse('orders:view_order', args=[pk]))
