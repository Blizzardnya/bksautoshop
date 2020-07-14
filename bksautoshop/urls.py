from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('orders/', include('orders.urls')),
    path('cart/', include('cart.urls')),
    path('accounts/', include([
        path('', include('accounts.urls')),
        path('', include('django.contrib.auth.urls')),
    ])),
    path('', include('bid.urls')),
    path('nested_admin/', include('nested_admin.urls')),
]

handler404 = 'bid.views.page_not_found_404_view'
handler500 = 'bid.views.internal_server_error_500_view'
