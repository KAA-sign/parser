# Generated by Django 2.2.7 on 2021-09-28 05:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aparser', '0006_product_published_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='published_date',
            field=models.CharField(max_length=100, verbose_name='Дата публикации'),
        ),
    ]
