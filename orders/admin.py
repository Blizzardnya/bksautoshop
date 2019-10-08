from django.contrib import admin
import nested_admin

from .models import Order, OrderItem, Container


class ContainerInline(nested_admin.NestedStackedInline):
    model = Container
    extra = 2


class OrderItemInline(nested_admin.NestedStackedInline):
    model = OrderItem
    raw_id_fields = ['product']
    inlines = [ContainerInline]
    extra = 2


@admin.register(Order)
class OrderAdmin(nested_admin.NestedModelAdmin):
    list_display = ['id', 'status', 'user', 'created', 'assembled', 'shipped', 'get_total_cost']
    list_filter = ['status', 'created', 'assembled', 'shipped']
    list_editable = ['status']
    inlines = [OrderItemInline]
