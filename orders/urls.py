from django.urls import path, include
from . import views

app_name = 'orders'

urlpatterns = [
    path('create/', views.create_order, name='order_create'),
]
