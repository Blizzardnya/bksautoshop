from rest_framework import serializers

from accounts.api.serializers import ShopUserSerializer
from bid.api.serializers import ProductSerializer
from orders.exceptions import NotNewOrderStatusException
from orders.models import Order, OrderItem


class OrderSerializer(serializers.ModelSerializer):
    """Сериальзация заявки"""
    user = ShopUserSerializer()
    order_items = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ('id', 'user', 'created', 'get_total_cost', 'status', 'order_items')
        read_only_fields = ('id', 'created')

    def update(self, instance, validated_data):
        """ Обновление статуса """
        if instance.status != 'N':
            raise NotNewOrderStatusException

        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance

    def get_order_items(self, instance):
        order_items = instance.items.all()
        return OrderItemSerializer(order_items, many=True).data


class OrderItemSerializer(serializers.ModelSerializer):
    """Сериализация строк заявки"""
    product = ProductSerializer()

    class Meta:
        model = OrderItem
        fields = ('product', 'price', 'quantity', 'get_cost')
