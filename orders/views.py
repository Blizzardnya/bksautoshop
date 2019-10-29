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
from .forms import ContainerOrderAddForm, ContainerWeightOrderItemAddForm, ContainerPieceOrderItemAddFormDis, \
    ContainerWeightOrderItemAddFormDis


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
    """ Просмотр заявки мерчендайзер и упаковщик """
    model = Order
    template_name = 'orders/merchandiser/view.html'
    permission_required = 'orders.view_order'


class SorterOrderView(LoginRequiredMixin, PermissionRequiredMixin, generic.DetailView):
    """ Просмотр заявки комплектовщик """
    model = Order
    template_name = 'orders/sorter/view.html'
    permission_required = 'accounts.is_sorter'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['container_order_form'] = ContainerOrderAddForm()
        return context


@login_required()
@permission_required('accounts.is_sorter')
def view_order_item_containers(request, pk, order_item_id):
    """ Просмотр контейнеров для обпределённой позиции в заявке """
    order_item = get_object_or_404(OrderItem, id=order_item_id)
    containers = [{'container': container,
                   'form': ContainerWeightOrderItemAddFormDis(initial={
                       'container_number': container.number,
                       'quantity': container.quantity
                   }) if container.order_item.product.unit.is_weight_type() else
                   ContainerPieceOrderItemAddFormDis(initial={
                       'container_number': container.number,
                       'quantity': int(container.quantity)
                   })} for container in order_item.containers.all()]
    form = ContainerWeightOrderItemAddForm()

    return render(request, 'orders/sorter/containers.html',
                  context={'containers': containers, 'order_id': pk, 'order_item': order_item,
                           'add_container_form': form})


@login_required()
@require_POST
@permission_required('accounts.is_sorter')
def set_order_container(request, pk):
    """ Добавление контейнера для каждой строки заявки """
    order = get_object_or_404(Order, id=pk)
    container_form = ContainerOrderAddForm(request.POST)
    assembled_products = []

    if container_form.is_valid():
        for item in order.items.all():
            container_total_quantity = item.get_total_quantity_in_containers()

            if container_total_quantity < item.quantity:
                container = Container.objects.filter(number=container_form.cleaned_data['container_number'],
                                                     order_item=item).first()
                if not container:
                    Container.objects.create(
                        order_item=item,
                        number=container_form.cleaned_data['container_number'],
                        quantity=item.quantity - container_total_quantity)
                else:
                    container.quantity = item.quantity
                    container.save(update_fields=['quantity'])
            else:
                assembled_products.append(item.product.name)

        if len(assembled_products) > 0:
            messages.add_message(request, messages.WARNING,
                                 f'Товары {assembled_products} укомплектованы в полном количестве')

        return HttpResponseRedirect(reverse('orders:sorter_view_order', args=[pk]))

    messages.add_message(request, 40, 'Контейнер не указан')
    return HttpResponseRedirect(reverse('orders:sorter_view_order', args=[pk]))


@login_required()
@require_POST
@permission_required('accounts.is_sorter')
def create_container(request, pk, order_item_id):
    """ Добавление контейнера """
    order_item = get_object_or_404(OrderItem, id=order_item_id)
    form = ContainerWeightOrderItemAddForm(request.POST)

    if form.is_valid():
        containers_total_quantity = order_item.get_total_quantity_in_containers()
        if order_item.quantity >= containers_total_quantity + form.cleaned_data['quantity']:
            container = Container.objects.filter(number=form.cleaned_data['container_number'],
                                                 order_item=order_item).first()
            if not container:
                Container.objects.create(
                    order_item=order_item,
                    number=form.cleaned_data['container_number'],
                    quantity=form.cleaned_data['quantity']
                )
            else:
                container.quantity += form.cleaned_data['quantity']
                container.save(update_fields=['quantity'])
        else:
            messages.add_message(request, messages.ERROR,
                                 'Количество товара в контейнере не может быть больше количества товара по заявке')
    else:
        messages.add_message(request, messages.ERROR, 'Введены некоректные данные')

    return HttpResponseRedirect(reverse('orders:order_item_containers', args=[pk, order_item_id]))


@login_required()
@require_POST
@permission_required('accounts.is_sorter')
def update_container(request, pk, order_item_id, container_id):
    """ Обновление контейнера """
    container = get_object_or_404(Container, id=container_id)
    order_item = container.order_item

    if container.order_item.product.unit.is_weight_type():
        form = ContainerWeightOrderItemAddFormDis(request.POST)
    else:
        form = ContainerPieceOrderItemAddFormDis(request.POST)

    if form.is_valid():
        containers_total_quantity = order_item.get_total_quantity_in_containers()

        if order_item.quantity >= containers_total_quantity - container.quantity + form.cleaned_data['quantity']:
            container.quantity = form.cleaned_data['quantity']
            container.save(update_fields=['quantity'])
            messages.add_message(request, messages.SUCCESS, 'Контейнер обновлён')
        else:
            messages.add_message(request, messages.ERROR,
                                 'Количество товара в контейнере не может быть больше количества товара по заявке')
    else:
        messages.add_message(request, messages.ERROR, 'Введены некоректные данные')

    return HttpResponseRedirect(reverse('orders:order_item_containers', args=[pk, order_item_id]))


@login_required()
@permission_required('accounts.is_sorter')
def delete_container(request, pk, order_item_id, container_id):
    """ Удаление контейнера """
    container = get_object_or_404(Container, id=container_id)
    container.delete()
    return HttpResponseRedirect(reverse('orders:order_item_containers', args=[pk, order_item_id]))


@login_required()
@permission_required('accounts.is_packer')
def packer_product_list(request):
    """ Просмотр списка заявок для упаковщика """
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
    """ Просмотр списка заявок для комплектовщика """
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
            status__in=(Order.PROCESSED, Order.ASSEMBLED), created__lte=date
        ).order_by('-created')


@login_required()
@permission_required('accounts.is_sorter')
def set_order_as_shipped(request, pk):
    """ Изменение статуса заявки на отправлено """
    order = get_object_or_404(Order, id=pk)

    if order.status == Order.PROCESSED:
        messages.add_message(request, 40, 'Заявка всё ещё не укомплектована')
        return HttpResponseRedirect(reverse('orders:view_order', args=[pk]))

    order.status = Order.SHIPPED
    order.shipped = timezone.now()
    order.save()
    return HttpResponseRedirect(reverse('orders:sorter_view_order', args=[pk]))
