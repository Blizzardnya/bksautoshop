from rest_framework import permissions
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.exceptions import InvalidOrderStatusException
from orders.services.order_services import get_orders_by_status
from .serializers import OrderSerializer


class OrdersByStatusAPIView(APIView):
    """Заявки по статусу"""
    permission_classes = [permissions.IsAuthenticated, ]
    parser_classes = (JSONParser, )

    def get(self, request):
        try:
            serializer = OrderSerializer(get_orders_by_status(request.GET.get('status')), many=True)
        except (InvalidOrderStatusException, KeyError) as err:
            return Response({'message': str(err)}, status=400)

        return Response({'orders': serializer.data})
