from django.urls import path, include
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.OrderListView.as_view(), name='list_orders'),
    path('<int:pk>/', views.OrderView.as_view(), name='view_order'),
    path('create/', views.create_order, name='order_create'),
    path('packer/', views.packer_product_list, name='packer_list_orders'),
]
