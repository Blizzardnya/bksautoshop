from django.urls import path, include
from . import views

app_name = 'bid'

urlpatterns = [
    path('', views.index, name='index'),
]
