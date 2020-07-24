from rest_framework import permissions
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.views import APIView

from bid.models import Product
from .serializers import ProductSerializer


class PrioductsApiView(APIView):
    """ Товар """
    permission_classes = [permissions.IsAuthenticated, ]
    parser_classes = (JSONParser,)

    def get(self, request, pk):
        try:
            serializer = ProductSerializer(Product.objects.get(pk=pk))
            return Response({'product': serializer.data}, status=200)
        except Product.DoesNotExist:
            return Response({'error': 'Товар не найдена'}, status=404)

    def post(self, request):
        try:
            data = request.data.get('product')
            serializer = ProductSerializer(data=data)

            if serializer.is_valid(raise_exception=True):
                product = serializer.save()
                return Response({'success': f'Товар {product.name} создан'}, status=200)
        except ValidationError:
            return Response({'error': 'Данные не прошли проверку'}, status=400)

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
        except ValidationError:
            return Response({'error': 'Данные не прошли проверку'}, status=400)
