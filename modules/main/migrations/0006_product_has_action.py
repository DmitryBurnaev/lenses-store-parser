# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-29 14:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_auto_20160825_1725'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='has_action',
            field=models.BooleanField(default=False, verbose_name='Акционный'),
        ),
    ]