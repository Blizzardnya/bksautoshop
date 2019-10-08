from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import ShopUser, StockUser


class ShopUserInLine(admin.StackedInline):
    model = ShopUser
    raw_id_fields = ['shop']


class StockUserInLine(admin.StackedInline):
    model = StockUser
    raw_id_fields = ['stock']


class SystemUserAdmin(UserAdmin):
    list_display = ['username', 'first_name', 'last_name']
    inlines = (ShopUserInLine, StockUserInLine)


admin.site.unregister(User)
admin.site.register(User, SystemUserAdmin)
