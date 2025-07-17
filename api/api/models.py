from django.db import models
from django.urls import reverse


class Categories(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Категория товара')
    slug = models.SlugField(max_length=250, unique=True, blank=True, null=True, verbose_name='URL')
    image = models.ImageField(upload_to='categories', blank=True, null=True, verbose_name='Изображение')

    class Meta:
        db_table = 'categories'
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['id']

    def __str__(self):
        return self.name


class Brands(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Бренд')
    slug = models.SlugField(max_length=250, unique=True, blank=True, null=True, verbose_name='URL')

    class Meta:
        db_table = 'brands'
        verbose_name = 'Бренд'
        verbose_name_plural = 'Бренды'
        ordering = ['name']

    def __str__(self):
        return self.name


class Products(models.Model):
    name = models.CharField(max_length=300, unique=True, verbose_name='Название')
    slug = models.SlugField(max_length=250, unique=True, blank=True, null=True, verbose_name='URL')
    #time_create = models.DateField(verbose_name='Дата публикации')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    image = models.ImageField(upload_to='products', blank=True, null=True, verbose_name='Фото')
    price = models.DecimalField(default=0.00, max_digits=12, decimal_places=2, verbose_name='Цена')
    discount = models.DecimalField(default=0.00, max_digits=4, decimal_places=2, verbose_name='Скидка в %')
    quantity = models.PositiveIntegerField(default=0, verbose_name=' Количество')
    brand = models.ForeignKey('Brands', on_delete=models.PROTECT, verbose_name='Бренд')
    category = models.ForeignKey('Categories', on_delete=models.PROTECT, verbose_name='Категория')

    class Meta:
        db_table = 'products'
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ('id',)
        indexes = [
            models.Index(fields=['id', 'slug']),
            models.Index(fields=['name']),
        ]
        #ordering = ('-time_create',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('products:product', kwargs={'product_slug': self.slug})

    def display_id(self):
        return f'{self.id:05}'

    def sell_price(self):
        if self.discount:
            return round(self.price - self.price*self.discount/100, 2)
        return self.price

    @property
    def get_images(self):
        return self.images.all()


class Characteristics(models.Model):

    CHOICE_MAIN_CAMERA = [(8, 8), (12, 12), (32, 32), (48, 48), (50, 50), (64, 64), (100, 100),  (108, 108), (200, 200)]
    CHOICE_BUILT_IN_MEMORY = [(64, 64), (128, 128), (256, 256), (512, 512), (1024, 1024)]
    CHOICE_RANDOM_ACCESS_MEMORY = [(3, 3), (4, 4), (6, 6), (8, 8), (12, 12), (16, 16)]

    product = models.OneToOneField('Products', on_delete=models.CASCADE, primary_key=True, verbose_name='Продукт')
    operating_system = models.CharField(max_length=70, blank=True, null=True, verbose_name='Операционная система')
    type_operating_system = models.CharField(max_length=70, blank=True, null=True,
                                             verbose_name='Тип операционной системы')
    processor = models.CharField(max_length=70, blank=True, null=True, verbose_name='Процессор')
    processor_frequency = models.CharField(max_length=70, blank=True, null=True, verbose_name='Частота процессора')
    number_of_cores = models.CharField(max_length=70, blank=True, null=True, verbose_name='Количество ядер')
    screen_diagonal = models.DecimalField(default=0.00, max_digits=7, decimal_places=2, verbose_name='Диагональ экрана, дюймы')
    display_features = models.PositiveIntegerField(blank=True, null=True, verbose_name='Особенности дисплея, Гц')
    # main_camera = models.PositiveIntegerField(blank=True, null=True, verbose_name='Основная камера, Мп')
    main_camera = models.PositiveIntegerField(choices=CHOICE_MAIN_CAMERA, blank=True, null=True, verbose_name='Основная камера, Мп')
    front_camera = models.PositiveIntegerField(blank=True, null=True, verbose_name='Фронтальная камера, Мп')
    video_resolution = models.PositiveIntegerField(blank=True, null=True, verbose_name='Разрешение видео, К')
    built_in_memory = models.PositiveIntegerField(choices=CHOICE_BUILT_IN_MEMORY, blank=True, null=True, verbose_name='Объем встроенной памяти, ГБ')
    random_access_memory = models.PositiveIntegerField(choices=CHOICE_RANDOM_ACCESS_MEMORY, blank=True, null=True, verbose_name='Объем оперативной памяти, ГБ')
    quantity_of_SIM = models.PositiveIntegerField(blank=True, null=True, verbose_name='Количество SIM карт')
    sim_card_type = models.CharField(max_length=20, blank=True, null=True, verbose_name='Тип SIM карты')
    color = models.CharField(max_length=30, blank=True, null=True, verbose_name='Цвет изделия')
    dimensions = models.CharField(max_length=70, blank=True, null=True, verbose_name='Габариты')
    weight = models.PositiveIntegerField(blank=True, null=True, verbose_name='Вес, г')
    battery_capacity = models.PositiveIntegerField(blank=True, null=True, verbose_name='Емкость аккумулятора, мАч')
    bluetooth = models.PositiveIntegerField(blank=True, null=True, verbose_name='Bluetooth')
    wi_fi = models.CharField(max_length=70, blank=True, null=True, verbose_name='Wi-Fi')
    connection_connector = models.CharField(max_length=50, blank=True, null=True, verbose_name='Разъем подключения')

    class Meta:
        db_table = 'characteristics'
        verbose_name = 'Характеристика'
        verbose_name_plural = 'Характеристики'


class ProductImage(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products', blank=True)
    # image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True)

    def __str__(self):
        return f'{self.product.name} - {self.image.name}'
