from django.urls import path, include

from bid.api import api

app_name = 'bid_api'

urlpatterns = [
    path('products/', include([
        path('', api.ProductsApiView.as_view()),
        path('<int:pk>', api.ProductApiView.as_view()),
    ])),
    path('categories/', api.CategoriesApiView.as_view()),
]
