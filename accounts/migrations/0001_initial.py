# Generated by Django 2.2.14 on 2020-07-06 09:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('bid', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='StockUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(blank=True, max_length=13, null=True, verbose_name='Телефон')),
                ('stock', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='bid.Stock', verbose_name='Склад')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Пользователь склада',
                'verbose_name_plural': 'Пользователи складов',
                'permissions': (('is_packer', 'Фасовщик'), ('is_sorter', 'Комплектовщик')),
            },
        ),
        migrations.CreateModel(
            name='ShopUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(blank=True, max_length=13, null=True, verbose_name='Телефон')),
                ('shop', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='bid.Shop', verbose_name='Торговый объект')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Пользователь магазина',
                'verbose_name_plural': 'Пользователи магазинов',
                'permissions': (('is_merchandiser', 'Товаровед'),),
            },
        ),
    ]
