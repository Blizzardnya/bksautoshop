from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.views import generic
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.utils import Error

from cart.cart import Cart
from accounts.models import ShopUser
from .models import Order, OrderItem, Container
from .forms import (ContainerOrderAddForm, ContainerWeightOrderItemAddForm, ContainerPieceOrderItemAddForm,
                    ContainerPieceOrderItemAddFormDisabled, ContainerWeightOrderItemAddFormDisabled)
from .services import (create_order_service, set_container_to_order_item_service, update_container_quantity_service,
                       set_container_to_order_service, delete_container_service, set_order_as_packed_service,
                       set_order_item_as_packed_service, set_order_as_shipped_service)
from .exceptions import ContainerOverflowException, NotPackedException, NotSortedException


@login_required()
@permission_required('orders.add_order')
def create_order(request):
    """ Создание заявки """
    if request.method == 'POST':
        cart = Cart(request.session)

        if len(cart) == 0:
            messages.add_message(request, messages.ERROR, 'Ваша корзина пуста.')
            return render(request, 'orders/merchandiser/create.html')
        try:
            order = create_order_service(request.user, cart)
        except Error:
            messages.add_message(request, messages.ERROR, 'При создании заявки произошла ошибка')
            return render(request, 'orders/merchandiser/create.html')
        except ShopUser.DoesNotExist:
            messages.add_message(request, messages.ERROR, f'Пользователь магазина для {str(request.user)} не найден')
            return render(request, 'orders/merchandiser/create.html')

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


class MerchandiserOrderView(LoginRequiredMixin, PermissionRequiredMixin, generic.DetailView):
    """ Просмотр заявки мерчендайзер """
    model = Order
    template_name = 'orders/merchandiser/view.html'
    permission_required = 'orders.view_order'


class PackerOrderView(LoginRequiredMixin, PermissionRequiredMixin, generic.DetailView):
    """ Просмотр заявки упаковщик """
    model = Order
    template_name = 'orders/packer/view.html'
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
    """ Просмотр контейнеров для определённой позиции в заявке """
    order_item = get_object_or_404(OrderItem, id=order_item_id)
    containers = [{'container': container,
                   'form': ContainerWeightOrderItemAddFormDisabled(initial={
                       'container_number': container.number,
                       'quantity': container.quantity
                   }) if container.order_item.product.unit.is_weight_type() else
                   ContainerPieceOrderItemAddFormDisabled(initial={
                       'container_number': container.number,
                       'quantity': int(container.quantity)
                   })} for container in order_item.containers.all()]

    quantity_in_containers = order_item.get_total_quantity_in_containers()

    if order_item.product.unit.is_weight_type():
        form = ContainerWeightOrderItemAddForm(initial={'quantity': order_item.quantity - quantity_in_containers})
    else:
        form = ContainerPieceOrderItemAddForm(initial={'quantity': int(order_item.quantity - quantity_in_containers)})

    return render(
        request, 'orders/sorter/containers.html',
        context={'containers': containers, 'order_id': pk, 'order_item': order_item, 'add_container_form': form}
    )


@login_required()
@require_POST
@permission_required('accounts.is_sorter')
def set_container_to_order(request, pk):
    """ Добавление контейнера для каждой строки заявки """
    container_form = ContainerOrderAddForm(request.POST)

    if container_form.is_valid():
        try:
            assembled_products, not_packed = set_container_to_order_service(
                pk, container_form.cleaned_data['container_number']
            )

            if assembled_products:
                messages.add_message(request, messages.WARNING,
                                     f'Товары {assembled_products} укомплектованы в полном количестве')

            if not_packed:
                messages.add_message(request, messages.ERROR, f'Товары {not_packed} ещё не упакованы')
        except Order.DoesNotExist:
            messages.add_message(request, messages.ERROR, f'Заявки с идентификатором {str(pk)} не существует')
    else:
        messages.add_message(request, messages.ERROR, 'Контейнер не указан')

    return HttpResponseRedirect(reverse('orders:sorter_view_order', args=[pk]))


@login_required()
@require_POST
@permission_required('accounts.is_sorter')
def set_container_to_order_item(request, pk, order_item_id):
    """ Добавление контейнера к строке заявки"""
    form = ContainerWeightOrderItemAddForm(request.POST)

    if form.is_valid():
        try:
            set_container_to_order_item_service(form.cleaned_data['container_number'], order_item_id,
                                                form.cleaned_data['quantity'])
        except (ContainerOverflowException, NotPackedException) as err:
            messages.add_message(request, messages.ERROR, str(err))
        except OrderItem.DoesNotExist:
            messages.add_message(request, messages.ERROR, f'В заявке нет строки с идентификатором {str(order_item_id)}')
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

    if order_item.product.unit.is_weight_type():
        form = ContainerWeightOrderItemAddFormDisabled(request.POST)
    else:
        form = ContainerPieceOrderItemAddFormDisabled(request.POST)

    if form.is_valid():
        containers_total_quantity = order_item.get_total_quantity_in_containers()

        if order_item.quantity >= containers_total_quantity - container.quantity + form.cleaned_data['quantity']:
            update_container_quantity_service(container, form.cleaned_data['quantity'], False)
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
    try:
        delete_container_service(container_id)
    except Container.DoesNotExist:
        messages.add_message(request, messages.ERROR, f'Контейнера с идентификатором {str(container_id)} не существует')

    return HttpResponseRedirect(reverse('orders:order_item_containers', args=[pk, order_item_id]))


@login_required()
@permission_required('accounts.is_packer')
def packer_product_list(request):
    """ Просмотр списка заявок для упаковщика """
    orders_list = Order.orders_for_packer.all()

    paginator = Paginator(orders_list, 12)
    page = request.GET.get('page')
    orders = paginator.get_page(page)

    return render(request, 'orders/packer/list.html', {'orders': orders})


@login_required()
@permission_required('accounts.is_packer')
def set_order_as_packed(request, pk):
    """ Пометить заявку с весовым товаром как упакованную """
    try:
        set_order_as_packed_service(pk)
    except Order.DoesNotExist:
        messages.add_message(request, messages.ERROR, f'Заявки с идентификатором {str(pk)} не существует')

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required()
@permission_required('accounts.is_packer')
def set_order_item_as_packed(request, order_item_id):
    """ Пометить строку заявки с весовым товаром как упакованную """
    try:
        set_order_item_as_packed_service(order_item_id)
    except OrderItem.DoesNotExist:
        messages.add_message(request, messages.ERROR, f'В заявке нет строки с идентификатором {str(order_item_id)}')

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


class SorterOrderListView(LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
    """ Просмотр списка заявок для комплектовщика """
    model = Order
    context_object_name = 'orders'
    template_name = 'orders/sorter/list.html'
    paginate_by = 12
    permission_required = 'accounts.is_sorter'

    def get_queryset(self):
        return Order.orders_for_sorter.order_by('-created')


@login_required()
@permission_required('accounts.is_sorter')
def set_order_as_shipped(request, pk):
    """ Изменение статуса заявки на отправлено """
    try:
        set_order_as_shipped_service(pk)
    except NotSortedException as err:
        messages.add_message(request, messages.ERROR, str(err))
        return HttpResponseRedirect(reverse('orders:sorter_view_order', args=[pk]))
    except Order.DoesNotExist:
        messages.add_message(request, messages.ERROR, f'Заявки с идентификатором {str(pk)} не существует')
        return HttpResponseRedirect(reverse('orders:sorter_view_order', args=[pk]))

    return HttpResponseRedirect(reverse('orders:sorter_list_orders'))
