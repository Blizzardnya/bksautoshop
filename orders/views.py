from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.paginator import Paginator
from django.db.utils import Error
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import generic
from django.views.decorators.http import require_POST

from accounts.models import ShopUser
from cart.cart import Cart
from .exceptions import ContainerOverflowException, NotPackedException, NotSortedException, CartIsEmptyException
from .forms import (AddContainerToOrderForm, AddContainerToOrderItemForm)
from .models import Order, OrderItem, Container
from .services.container_services import (set_container_to_order_service, set_container_to_order_item_service,
                                          delete_container_service, update_order_item_container_service,
                                          get_order_item_and_containers_with_form)
from .services.order_services import (create_order_service, set_order_as_packed_service,
                                      set_order_as_shipped_service, set_order_item_as_packed_service,
                                      get_orders_by_shop_user_service)


@login_required()
@permission_required('orders.add_order')
def create_order_view(request):
    """ Создание заявки """
    try:
        order = create_order_service(request.user, Cart(request.session))
        return render(request, 'orders/merchandiser/created.html', context={'order': order})
    except Error:
        messages.error(request, 'При создании заявки произошла ошибка')
    except ShopUser.DoesNotExist:
        messages.error(request, f'Пользователь магазина для {str(request.user)} не найден')
    except CartIsEmptyException as cart_exc:
        messages.warning(request, str(cart_exc))

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


class MerchandiserOrderListView(LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
    """ Просмотр списка заявок пользователя """
    model = Order
    context_object_name = 'orders'
    template_name = 'orders/merchandiser/list.html'
    paginate_by = 12
    permission_required = 'accounts.is_merchandiser'

    def get_queryset(self):
        orders = []

        try:
            orders = get_orders_by_shop_user_service(self.request.user)
        except ShopUser.DoesNotExist:
            messages.error(self.request, f'Пользователь магазина для {str(self.request.user)} не найден')

        return orders


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
        context['container_order_form'] = AddContainerToOrderForm()
        return context


@login_required()
@permission_required('accounts.is_sorter')
def order_item_containers_view(request, pk, order_item_id):
    """ Просмотр контейнеров для определённой позиции в заявке """
    try:
        order_item, containers = get_order_item_and_containers_with_form(order_item_id)
        form = AddContainerToOrderItemForm(
            initial={'quantity': order_item.missing_quantity_in_containers},
            is_weight_type=order_item.product.unit.is_weight_type
        )
    except OrderItem.DoesNotExist:
        messages.error(request, f'В заявке нет строки с идентификатором {str(order_item_id)}')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    return render(
        request, 'orders/sorter/containers.html',
        context={'containers': containers, 'order_id': pk, 'order_item': order_item, 'add_container_form': form}
    )


@login_required()
@require_POST
@permission_required('accounts.is_sorter')
def set_container_to_order_view(request, pk):
    """ Добавление контейнера для каждой строки заявки """
    container_form = AddContainerToOrderForm(request.POST)

    if container_form.is_valid():
        try:
            not_packed = set_container_to_order_service(pk, container_form.cleaned_data['container_number'])

            if not_packed:
                messages.error(request, f'Товары {not_packed} ещё не упакованы')
        except Order.DoesNotExist:
            messages.error(request, f'Заявки с идентификатором {str(pk)} не существует')
    else:
        messages.error(request, 'Контейнер не указан')

    return HttpResponseRedirect(reverse('orders:sorter_view_order', args=[pk]))


@login_required()
@require_POST
@permission_required('accounts.is_sorter')
def set_container_to_order_item_view(request, pk, order_item_id):
    """ Добавление контейнера к строке заявки"""
    form = AddContainerToOrderItemForm(
        request.POST,
        is_weight_type=True
    )

    if form.is_valid():
        try:
            set_container_to_order_item_service(form.cleaned_data['container_number'], order_item_id,
                                                form.cleaned_data['quantity'])
        except (ContainerOverflowException, NotPackedException) as err:
            messages.error(request, err)
        except OrderItem.DoesNotExist:
            messages.error(request, f'В заявке нет строки с идентификатором {str(order_item_id)}')
    else:
        messages.error(request, 'Введены некоректные данные')

    return HttpResponseRedirect(reverse('orders:order_item_containers', args=[pk, order_item_id]))


@login_required()
@require_POST
@permission_required('accounts.is_sorter')
def update_container_view(request, pk, order_item_id, container_id):
    """ Обновление контейнера """
    form = AddContainerToOrderItemForm(
        request.POST,
        disabled_number=True,
        is_weight_type=True
    )

    if form.is_valid():
        try:
            update_order_item_container_service(container_id, form.cleaned_data['quantity'])
            messages.success(request, 'Контейнер обновлён')
        except Container.DoesNotExist:
            messages.error(request, f'Контейнера с идентификатором {str(container_id)} не существует')
        except ContainerOverflowException as err:
            messages.error(request, err)
    else:
        messages.add_message(request, messages.ERROR, 'Введены некоректные данные')

    return HttpResponseRedirect(reverse('orders:order_item_containers', args=[pk, order_item_id]))


@login_required()
@permission_required('accounts.is_sorter')
def delete_container_view(request, pk, order_item_id, container_id):
    """ Удаление контейнера """
    try:
        delete_container_service(container_id)
    except Container.DoesNotExist:
        messages.error(request, f'Контейнера с идентификатором {str(container_id)} не существует')

    return HttpResponseRedirect(reverse('orders:order_item_containers', args=[pk, order_item_id]))


@login_required()
@permission_required('accounts.is_packer')
def packer_product_list_view(request):
    """ Просмотр списка заявок для упаковщика """
    paginator = Paginator(Order.orders_for_packer.all(), 12)
    page = request.GET.get('page')
    orders = paginator.get_page(page)

    return render(request, 'orders/packer/list.html', {'orders': orders})


@login_required()
@permission_required('accounts.is_packer')
def set_order_as_packed_view(request, pk):
    """ Пометить заявку с весовым товаром как упакованную """
    try:
        set_order_as_packed_service(pk)
    except Order.DoesNotExist:
        messages.error(request, f'Заявки с идентификатором {str(pk)} не существует')

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required()
@permission_required('accounts.is_packer')
def set_order_item_as_packed_view(request, order_item_id):
    """ Пометить строку заявки с весовым товаром как упакованную """
    try:
        set_order_item_as_packed_service(order_item_id)
    except OrderItem.DoesNotExist:
        messages.error(request, f'В заявке нет строки с идентификатором {str(order_item_id)}')

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
def set_order_as_shipped_view(request, pk):
    """ Изменение статуса заявки на отправлено """
    try:
        set_order_as_shipped_service(pk)
        return HttpResponseRedirect(reverse('orders:sorter_list_orders'))
    except NotSortedException as err:
        messages.error(request, err)
    except Order.DoesNotExist:
        messages.error(request, f'Заявки с идентификатором {str(pk)} не существует')

    return HttpResponseRedirect(reverse('orders:sorter_view_order', args=[pk]))
