# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-04-26 22:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0003_product_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='prices',
            field=models.BooleanField(default=True, verbose_name='prices enabled'),
        ),
    ]