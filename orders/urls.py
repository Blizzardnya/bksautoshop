from django.urls import path, include
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.MerchandiserOrderListView.as_view(), name='merchandiser_list_orders'),
    path('<int:pk>/', include([
        path('', views.OrderView.as_view(), name='view_order'),
        path('shipped/', views.set_order_as_shipped, name='shipped_order'),
    ])),
    path('create/', views.create_order, name='order_create'),
    path('packer/', views.packer_product_list, name='packer_list_orders'),
    path('sorter/', include([
        path('', views.SorterOrderListView.as_view(), name='sorter_list_orders'),
        path('<int:pk>/', include([
            path('', views.SorterOrderView.as_view(), name='sorter_view_order'),
            path('add_container/', views.set_order_container, name='add_container_order'),
            path('<int:order_item_id>/', include([
                path('', views.view_order_item_containers, name='order_item_containers'),
                path('<int:container_id>/update/', views.update_container, name='update_container'),
            ])),
        ])),
    ])),
]
