from rest_framework import serializers

from bid.exceptions import ProductAlreadyExistException
from bid.models import Product, Category, Unit, ProductMatrix


class CategorySerializer(serializers.ModelSerializer):
    """ Сериальзация категорий """

    class Meta:
        model = Category
        fields = ('id', 'name', 'root_category')


class ProductSerializer(serializers.ModelSerializer):
    """ Сериализация продуктов """

    class Meta:
        model = Product
        fields = ('barcode', 'name', 'category', 'matrix', 'storage_condition', 'unit', 'price')

    def create(self, validated_data):
        barcode = validated_data.pop('barcode')
        matrix = validated_data.pop('matrix')
        product, created = Product.objects.get_or_create(
            barcode=barcode,
            defaults={**validated_data}
        )

        if not created:
            raise ProductAlreadyExistException

        product.matrix.set(matrix)

        return product

    def update(self, instance, validated_data):
        instance.price = validated_data.get('price', instance.price)
        instance.save()
        return instance


class UnitSerializer(serializers.ModelSerializer):
    """ Сериализация мер исчисления """

    class Meta:
        model = Unit
        fields = ('id', 'name', 'short_name')


class ProductMatrixSerializer(serializers.ModelSerializer):
    """ Сериализация матриц товаров """

    class Meta:
        model = ProductMatrix
        fields = ('id', 'name')
