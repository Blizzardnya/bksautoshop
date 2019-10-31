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
    path('packer/', include([
        path('', views.packer_product_list, name='packer_list_orders'),
        path('<int:order_item_id>/UpdateItem', views.set_order_item_as_packed, name='update_order_item_packed'),
        path('<int:order_id>/UpdateOrder', views.set_order_as_packed, name='update_order_packed'),
    ])),
    path('sorter/', include([
        path('', views.SorterOrderListView.as_view(), name='sorter_list_orders'),
        path('<int:pk>/', include([
            path('', views.SorterOrderView.as_view(), name='sorter_view_order'),
            path('add_container/', views.set_order_container, name='add_container_order'),
            path('<int:order_item_id>/', include([
                path('', views.view_order_item_containers, name='order_item_containers'),
                path('containers/add/', views.create_container, name='add_container'),
                path('<int:container_id>/update/', views.update_container, name='update_container'),
                path('<int:container_id>/delete/', views.delete_container, name='delete_container'),
            ])),
        ])),
    ])),
]
