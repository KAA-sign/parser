# Generated by Django 2.2.7 on 2021-09-21 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aparser', '0004_product_currency'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='currency',
            field=models.TextField(blank=True, null=True, verbose_name='Валюта'),
        ),
    ]