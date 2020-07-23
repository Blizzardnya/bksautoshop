from rest_framework import serializers

from bid.models import Product, Category


class CategorySerializer(serializers.ModelSerializer):
    """Сериальзация категорий"""

    class Meta:
        model = Category
        fields = ('name', 'root_category')


class ProductSerializer(serializers.ModelSerializer):
    """Сериализация продуктов"""
    category = CategorySerializer()

    class Meta:
        model = Product
        fields = ('barcode', 'name', 'price', 'category')
