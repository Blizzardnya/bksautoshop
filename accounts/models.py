from django.db import models
from django.contrib.auth.models import User

from bid.models import Shop, Stock


class AbstractUser(models.Model):
    """ Абстрактная модель пользователя """
    user = models.OneToOneField(User, verbose_name="Пользователь", on_delete=models.CASCADE)
    phone = models.CharField("Телефон", max_length=13, null=True, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name


class ShopUser(AbstractUser):
    """ Модель пользователя магазина """
    shop = models.OneToOneField(Shop, verbose_name="Торговый объект", null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = "Пользователь магазина"
        verbose_name_plural = "Пользователи магазинов"
        permissions = (("is_merchandiser", "Товаровед"), )


class StockUser(AbstractUser):
    """ Модель пользователя склада """
    stock = models.ForeignKey(Stock, verbose_name="Склад", null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = "Пользователь склада"
        verbose_name_plural = "Пользователи складов"
        permissions = (("is_packer", "Фасовщик"), ("is_sorter", "Комплектовщик"))
