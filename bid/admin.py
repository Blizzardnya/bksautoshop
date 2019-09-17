from django.contrib import admin
from .models import *


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'barcode', 'unit', 'price']
    search_fields = ['name', 'barcode']
    fields = ['name', 'barcode', 'unit', 'price']


admin.site.register(Unit)
