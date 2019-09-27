from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import SystemUser


class SystemUserInLine(admin.StackedInline):
    model = SystemUser
    raw_id_fields = ['shop']


class SystemUserAdmin(UserAdmin):
    inlines = (SystemUserInLine, )


admin.site.unregister(User)
admin.site.register(User, SystemUserAdmin)
