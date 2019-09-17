from django.db import models
from django.contrib.auth.models import User
from bid.models import Shop


class SystemUser(models.Model):
    """ Модель пользователя системы """
    user = models.OneToOneField(User, verbose_name="Пользователь", on_delete=models.CASCADE)
    phone = models.CharField("Телефон", max_length=13, null=True, blank=True)
    shop = models.OneToOneField(Shop, verbose_name="Торговый объект", null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = "Пользователь системы"
        verbose_name_plural = "Пользователи системы"

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name
