from django.urls import path

from orders.api import orders_api

app_name = 'orders_api'

urlpatterns = [
    path('by_status', orders_api.OrdersByStatusAPIView.as_view()),
    path('<int:pk>', orders_api.OrderApiView.as_view()),
]
