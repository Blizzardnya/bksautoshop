from django.contrib import admin
from .models import Product, ProductMatrix, Category, Shop, Provider, Unit, Stock


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'root_category']
    list_filter = ('root_category',)
    raw_id_fields = ['root_category']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    empty_value_display = '(Основная)'
    ordering = ('root_category', 'name')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['barcode', 'name', 'category', 'unit', 'storage_condition', 'price', 'display_matrix']
    list_filter = ('storage_condition', 'created_at', 'updated_at')
    list_display_links = ('barcode', 'name')
    search_fields = ['name', 'barcode']
    raw_id_fields = ['category']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['name', 'stock_type']
    list_filter = ('stock_type',)
    list_display_links = ('name',)
    search_fields = ['name']


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ['name', 'UNP', 'branch_code', 'product_matrix', 'stock']
    list_filter = ('product_matrix',)
    list_display_links = ('name',)
    search_fields = ['name', 'UNP', 'branch_code']
    raw_id_fields = ['stock']


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ['name', 'UNP', 'branch_code']
    list_display_links = ('name',)
    search_fields = ['name', 'UNP', 'branch_code']


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ['name', 'short_name', 'type']
    list_display_links = ('name',)
    list_editable = ['type']
    search_fields = ['name']


admin.site.register(ProductMatrix)
