from django.urls import path, include

from bid.api import api

app_name = 'bid_api'

urlpatterns = [
    path('products/', include([
        path('', api.PrioductsApiView.as_view()),
        path('<int:pk>', api.PrioductsApiView.as_view()),
    ]))
]
