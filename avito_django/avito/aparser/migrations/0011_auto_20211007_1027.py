# Generated by Django 2.2.7 on 2021-10-07 07:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aparser', '0010_task_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='title',
            field=models.TextField(unique=True, verbose_name='Название задания'),
        ),
    ]
