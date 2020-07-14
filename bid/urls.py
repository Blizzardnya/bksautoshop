from django.urls import path, include

from . import views

app_name = 'bid'

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', include([
        path('', views.prepare_search, name='prepare_search'),
        path('<str:word>/', views.search_results, name='search_results'),
    ])),
    path('products/', views.product_list, name='product_list'),
    path('products/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
]
