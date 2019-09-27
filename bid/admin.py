from django.contrib import admin
from .models import Product, ProductMatrix, Category, Shop, Provider, Unit


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'root_category']
    raw_id_fields = ['root_category']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['barcode', 'name', 'category', 'unit', 'storage_condition', 'price']
    list_filter = ('created_at', 'updated_at')
    list_display_links = ('barcode', 'name')
    search_fields = ['name', 'barcode']
    raw_id_fields = ['category']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ['name', 'UNP', 'branch_code', 'shop_type', 'product_matrix']
    list_filter = ('shop_type', 'product_matrix')
    list_display_links = ('name',)
    search_fields = ['name', 'UNP', 'branch_code']


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ['name', 'UNP', 'branch_code']
    list_display_links = ('name',)
    search_fields = ['name', 'UNP', 'branch_code']


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ['name', 'short_name']
    list_display_links = ('name',)
    search_fields = ['name']


admin.site.register(ProductMatrix)
