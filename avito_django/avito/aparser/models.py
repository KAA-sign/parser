from django.db import models

class Product(models.Model):

    title = models.TextField(verbose_name='Заголовок')
    price = models.PositiveIntegerField(verbose_name='Цена')
    currency = models.TextField(verbose_name='Валюта')
    url = models.URLField(verbose_name='Ссылка на объявление', unique=True)


    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'


