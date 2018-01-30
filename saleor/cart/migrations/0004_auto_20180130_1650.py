# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-30 22:50
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0003_auto_20180130_1457'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='token',
            field=models.CharField(default=uuid.uuid4, max_length=128, primary_key=True, serialize=False, verbose_name='token'),
        ),
    ]
