from django.urls import path, include
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.MerchandiserOrderListView.as_view(), name='merchandiser_list_orders'),
    path('<int:pk>/', include([
        path('', views.OrderView.as_view(), name='view_order'),
        path('shipped/', views.set_order_as_shipped, name='shipped_order'),
        path('add_container/', views.ser_order_container, name='add_container_order'),
    ])),
    path('create/', views.create_order, name='order_create'),
    path('packer/', views.packer_product_list, name='packer_list_orders'),
    path('sorter/', views.SorterOrderListView.as_view(), name='sorter_list_orders'),
]
