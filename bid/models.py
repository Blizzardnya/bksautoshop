from django.db import models


class Unit(models.Model):
    """ Модель меры исчисления """
    name = models.CharField("Полное наименование меры исчисления", max_length=30)
    short_name = models.CharField("Краткое наименование меры исчисления", max_length=10)

    class Meta:
        verbose_name = 'Мера исчисления'
        verbose_name_plural = 'Меры исчисления'

    def __str__(self):
        return self.name


class ProductMatrix(models.Model):
    """ Модель матрицы товаров """
    name = models.CharField("Наименование матрицы", max_length=50)

    class Meta:
        verbose_name = 'Матрица товаров'
        verbose_name_plural = 'Матрицы товаров'

    def __str__(self):
        return self.name


class Category(models.Model):
    """ Модель категории товара """
    name = models.CharField("Наименование матрицы", max_length=80)
    root_category = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    """ Модель товара """
    barcode = models.CharField("Штрих-код", max_length=13)
    name = models.CharField("Наименование товара", max_length=150, db_index=True)
    slug = models.SlugField(max_length=150, unique=True, db_index=True)
    unit = models.ForeignKey(Unit, verbose_name="Мера исчисления", on_delete=models.PROTECT)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    matrix = models.ManyToManyField(ProductMatrix, verbose_name="Матрица товаров")
    category = models.ForeignKey(Category, on_delete=models.PROTECT)

    ORDINARY = 'O'
    COOLED = 'C'
    FROZEN = 'F'

    STORAGE_CONDITION = (
        (ORDINARY, 'Обычное'),
        (COOLED, 'Охлаждённое'),
        (FROZEN, 'Замороженное'),
    )

    storage_condition = models.CharField("Состояние хранения", max_length=1, choices=STORAGE_CONDITION,
                                         default=ORDINARY)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)

    class Meta:
        ordering = ('name', )
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.name


class Organization(models.Model):
    """ Абстрактная модель организации """
    name = models.CharField("Наименование организации", max_length=150, db_index=True)
    UNP = models.CharField("УНП", max_length=10)
    branch_code = models.CharField("Код филиала", max_length=4, null=True, blank=True)

    class Meta:
        abstract = True
        ordering = ('name', )

    def __str__(self):
        return self.name


class Shop(Organization):
    """ Модель торгового объекта """
    address = models.CharField("Адрес", max_length=150)
    shop_type = models.CharField("Формат объекта", max_length=1)
    product_matrix = models.ForeignKey(ProductMatrix, verbose_name="Матрица товаров", on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'Торговый объект'
        verbose_name_plural = 'Торговые объекты'


Shop._meta.get_field('name').verbose_name = 'Наименование торгового объекта'


class Provider(Organization):
    """ Модель поставщика """

    class Meta:
        verbose_name = 'Поставщик'
        verbose_name_plural = 'Поставщики'


Provider._meta.get_field('name').verbose_name = 'Наименование поставщика'
