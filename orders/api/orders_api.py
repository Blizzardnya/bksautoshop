from django.core.paginator import Paginator, EmptyPage
from rest_framework import permissions
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.views import APIView

from orders.exceptions import InvalidOrderStatusException, NotNewOrderStatusException
from orders.models import Order
from orders.services.order_services import get_orders_by_status
from .serializers import OrderSerializer


class OrdersAPIView(APIView):
    """Заявки"""
    permission_classes = [permissions.IsAuthenticated, ]
    parser_classes = (JSONParser,)

    def get(self, request):
        status = request.query_params.get('status')

        try:
            page = int(request.query_params.get('page', 1))
        except ValueError:
            return Response({'error': 'Некорректное значение параметра page'}, status=422)

        try:
            limit = int(request.query_params.get('limit', 50))
        except ValueError:
            return Response({'error': 'Некорректное значение параметра limit'}, status=422)

        try:
            if status is not None:
                orders = get_orders_by_status(status)
            else:
                orders = Order.objects.all()

            paginator = Paginator(orders, limit)

            try:
                orders_page = paginator.page(page)
            except EmptyPage:
                orders_page = paginator.page(paginator.num_pages)

            serializer = OrderSerializer(orders_page, many=True)
        except (InvalidOrderStatusException, KeyError) as err:
            return Response({'error': str(err)}, status=400)

        return Response({'orders': serializer.data}, status=200)


class OrderApiView(APIView):
    """ Заявка """
    permission_classes = [permissions.IsAuthenticated, ]
    parser_classes = (JSONParser,)

    def get(self, request, pk):
        try:
            serializer = OrderSerializer(Order.objects.get(pk=pk))
            return Response({'order': serializer.data}, status=200)
        except Order.DoesNotExist:
            return Response({'error': 'Заявка не найдена'}, status=404)

    def patch(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
            data = request.data.get('order')
            serializer = OrderSerializer(instance=order, data=data, partial=True)

            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response({'success': 'Статус заявки обновлён'}, status=200)
        except Order.DoesNotExist:
            return Response({'error': 'Заявка не найдена'}, status=404)
        except ValidationError:
            return Response({'error': 'Данные не прошли проверку'}, status=400)
        except NotNewOrderStatusException as err:
            return Response({'error': str(err)}, status=400)
