# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-25 11:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20160825_1259'),
    ]

    operations = [
        migrations.AddField(
            model_name='brand',
            name='remote_id',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='ID на сайте'),
        ),
        migrations.AddField(
            model_name='brand',
            name='url',
            field=models.URLField(blank=True, default='', verbose_name='Урл на сайте'),
        ),
        migrations.AddField(
            model_name='product',
            name='remote_id',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='ID на сайте'),
        ),
        migrations.AddField(
            model_name='product',
            name='url',
            field=models.URLField(blank=True, default='', verbose_name='Урл на сайте'),
        ),
    ]
