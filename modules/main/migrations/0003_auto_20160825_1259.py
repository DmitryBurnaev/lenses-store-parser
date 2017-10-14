# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-25 09:59
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20160720_1818'),
    ]

    operations = [
        migrations.CreateModel(
            name='ParseResultLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('date_updated', models.DateTimeField(auto_now=True, verbose_name='Дата обночления')),
                ('received_data', jsonfield.fields.JSONField(blank=True, null=True, verbose_name='Полученные данные')),
                ('changes', jsonfield.fields.JSONField(blank=True, null=True, verbose_name='Внесенные изменения')),
            ],
            options={
                'verbose_name': 'Результат парсинга',
                'verbose_name_plural': 'Результаты парсинга',
            },
        ),
        migrations.AddField(
            model_name='brand',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, default=None, verbose_name='Дата создания'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='brand',
            name='date_updated',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата обночления'),
        ),
        migrations.AddField(
            model_name='price',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, default=None, verbose_name='Дата создания'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='price',
            name='date_updated',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата обночления'),
        ),
        migrations.AddField(
            model_name='product',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, default=None, verbose_name='Дата создания'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='date_updated',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата обночления'),
        ),
    ]
