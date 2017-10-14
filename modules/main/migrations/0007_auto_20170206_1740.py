# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-02-06 14:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_product_has_action'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='price',
            options={'ordering': ('-date_created',), 'verbose_name': 'Цена за товар', 'verbose_name_plural': 'Цены за товар'},
        ),
        migrations.AddField(
            model_name='parseresultlog',
            name='finish_time',
            field=models.DateTimeField(blank=True, default=None, null=True, verbose_name='Время окончания парсинга'),
        ),
    ]
