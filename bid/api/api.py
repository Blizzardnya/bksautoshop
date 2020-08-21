from django.core.paginator import Paginator, EmptyPage
from rest_framework import permissions
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.views import APIView

from bid.models import Product, Category
from bid.services import get_categories_by_root_category_service
from .serializers import ProductSerializer, CategorySerializer


class ProductApiView(APIView):
    """ Товар """
    permission_classes = [permissions.IsAuthenticated, ]
    parser_classes = (JSONParser,)

    def get(self, request, pk):
        try:
            serializer = ProductSerializer(Product.objects.get(pk=pk))
            return Response({'product': serializer.data}, status=200)
        except Product.DoesNotExist:
            return Response({'error': 'Товар не найден'}, status=404)

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


class ProductsApiView(APIView):
    """ Товары """
    permission_classes = [permissions.IsAuthenticated, ]
    parser_classes = (JSONParser,)

    def get(self, request):
        try:
            category_id = request.query_params.get('category')

            try:
                page = int(request.query_params.get('page', 1))
            except ValueError:
                return Response({'error': 'Некорректное значение параметра page'}, status=422)

            try:
                limit = int(request.query_params.get('limit', 50))
            except ValueError:
                return Response({'error': 'Некорректное значение параметра limit'}, status=422)

            if category_id is not None:
                category = Category.objects.get(category_id)
                products = Product.objects.filter(category=category)
            else:
                products = Product.objects.all()

            paginator = Paginator(products, limit)

            try:
                products_page = paginator.page(page)
            except EmptyPage:
                products_page = paginator.page(paginator.num_pages)

            serializer = ProductSerializer(products_page, many=True)
            return Response({'products': serializer.data}, status=200)
        except Product.DoesNotExist:
            return Response({'error': 'Товар не найден'}, status=404)
        except Category.DoesNotExist:
            return Response({'error': 'Категория не найдена'}, status=404)

    def post(self, request):
        try:
            data = request.data.get('product')
            serializer = ProductSerializer(data=data)

            if serializer.is_valid(raise_exception=True):
                product = serializer.save()
                return Response({'success': f'Товар {product.name} создан'}, status=200)
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

            get_nested = bool(request.query_params.get('get_all', False))

            categories = get_categories_by_root_category_service(root_category, get_nested)
            serializer = CategorySerializer(categories, many=True)
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
