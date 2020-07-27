from rest_framework import permissions
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.views import APIView

from bid.models import Product, Category
from bid.services import get_categories_by_root_category_service
from .serializers import ProductSerializer, CategorySerializer


class ProductsApiView(APIView):
    """ Товар """
    permission_classes = [permissions.IsAuthenticated, ]
    parser_classes = (JSONParser,)

    def get(self, request, pk):
        try:
            serializer = ProductSerializer(Product.objects.get(pk=pk))
            return Response({'product': serializer.data}, status=200)
        except Product.DoesNotExist:
            return Response({'error': 'Товар не найден'}, status=404)

    def post(self, request):
        try:
            data = request.data.get('product')
            serializer = ProductSerializer(data=data)

            if serializer.is_valid(raise_exception=True):
                product = serializer.save()
                return Response({'success': f'Товар {product.name} создан'}, status=200)
        except ValidationError as v_err:
            return Response({'error': {'head': 'Данные не прошли проверку', 'message': str(v_err)}}, status=400)

    def patch(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
            data = request.data.get('product')
            serializer = ProductSerializer(instance=product, data=data, partial=True)

            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response({'success': 'Цена обновлена'}, status=200)
        except Product.DoesNotExist:
            return Response({'error': 'Товар не найдена'}, status=404)
        except ValidationError as v_err:
            return Response({'error': {'head': 'Данные не прошли проверку', 'message': str(v_err)}}, status=400)


class CategoriesApiView(APIView):
    """ Категории товара """
    permission_classes = [permissions.IsAuthenticated, ]
    parser_classes = (JSONParser,)

    def get(self, request):
        try:
            root_category_id = request.query_params.get('root_category_id', None)
            if root_category_id:
                root_category = Category.objects.get(id=root_category_id)
            else:
                root_category = None
            get_all = bool(request.query_params.get('get_all', False))
            serializer = CategorySerializer(get_categories_by_root_category_service(root_category, get_all), many=True)
            return Response({'categories': serializer.data}, status=200)
        except Category.DoesNotExist:
            return Response({'error': 'Категория не найдена'}, status=404)

    def post(self, request):
        try:
            data = request.data.get('category')
            serializer = CategorySerializer(data=data)

            if serializer.is_valid(raise_exception=True):
                category = serializer.save()
                return Response({'success': f'Категория {category.name} создана'}, status=200)
        except ValidationError as v_err:
            return Response({'error': {'head': 'Данные не прошли проверку', 'message': str(v_err)}}, status=400)
