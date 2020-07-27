from pytils.translit import slugify
from rest_framework import serializers
from rest_framework.serializers import ValidationError

from bid.models import Product, Category, Unit, ProductMatrix


class CategorySerializer(serializers.ModelSerializer):
    """ Сериальзация категорий """

    class Meta:
        model = Category
        fields = ('id', 'name', 'root_category')

    def create(self, validated_data):
        name = validated_data.pop('name')
        category, created = Category.objects.get_or_create(
            name=name,
            defaults={'slug': slugify(name), 'root_category': validated_data.get('root_category')}
        )

        if not created:
            raise ValidationError('Категория с таким именем уже существует')

        return category


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
            defaults={'slug': slugify(validated_data.get('name')), **validated_data}
        )

        if not created:
            raise ValidationError('Товар с таким штрих-кодом уже существует')

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
