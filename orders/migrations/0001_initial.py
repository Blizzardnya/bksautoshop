# Generated by Django 2.2.14 on 2020-07-06 09:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        ('bid', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('assembled', models.DateTimeField(blank=True, null=True, verbose_name='Дата комплектовки')),
                ('shipped', models.DateTimeField(blank=True, null=True, verbose_name='Дата отгрузки')),
                ('status', models.CharField(choices=[('N', 'Новый'), ('P', 'Обработан'), ('A', 'Укомплектован'), ('S', 'Отправлен')], default='N', max_length=1, verbose_name='Статус')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.ShopUser', verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Заявка',
                'verbose_name_plural': 'Заявки',
                'ordering': ('-created',),
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена')),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Количество')),
                ('packed', models.BooleanField(default=True, verbose_name='Упаковано')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='orders.Order', verbose_name='Заявка')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_item', to='bid.Product', verbose_name='Товар')),
            ],
            options={
                'verbose_name': 'Строка заявки',
                'verbose_name_plural': 'Строки заявки',
            },
        ),
        migrations.CreateModel(
            name='Container',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=20, verbose_name='Номер контейнера')),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Количество')),
                ('order_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='containers', to='orders.OrderItem', verbose_name='Товар')),
            ],
            options={
                'verbose_name': 'Контейнер',
                'verbose_name_plural': 'Контейнеры',
            },
        ),
    ]
