from django.contrib.auth.models import User
from rest_framework import serializers

from accounts.models import ShopUser


class UserSerializer(serializers.ModelSerializer):
    """Сериальзация пользователей"""

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name')


class ShopUserSerializer(serializers.ModelSerializer):
    """Сериализация пользователей магазина"""
    user = UserSerializer()

    class Meta:
        model = ShopUser
        fields = ('user',)
