from django.urls import path, include

from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.MerchandiserOrderListView.as_view(), name='merchandiser_list_orders'),
    path('<int:pk>/', include([
        path('', views.MerchandiserOrderView.as_view(), name='merchandiser_view_order'),
        path('shipped/', views.set_order_as_shipped_view, name='shipped_order'),
    ])),
    path('create/', views.create_order_view, name='order_create'),
    path('packer/', include([
        path('', views.packer_product_list_view, name='packer_list_orders'),
        path('<int:pk>', include([
            path('', views.PackerOrderView.as_view(), name='packer_view_order'),
            path('UpdateOrder/', views.set_order_as_packed_view, name='update_order_packed'),
        ])),
        path('<int:order_item_id>/UpdateItem', views.set_order_item_as_packed_view, name='update_order_item_packed'),
    ])),
    path('sorter/', include([
        path('', views.SorterOrderListView.as_view(), name='sorter_list_orders'),
        path('<int:pk>/', include([
            path('', views.SorterOrderView.as_view(), name='sorter_view_order'),
            path('add_container/', views.set_container_to_order_view, name='add_container_order'),
            path('<int:order_item_id>/', include([
                path('', views.order_item_containers_view, name='order_item_containers'),
                path('containers/add/', views.set_container_to_order_item_view, name='add_container'),
                path('<int:container_id>/update/', views.update_container_view, name='update_container'),
                path('<int:container_id>/delete/', views.delete_container_view, name='delete_container'),
            ])),
        ])),
    ])),
]
