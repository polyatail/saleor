# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-30 02:18
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0003_companyfield'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='CompanyField',
            new_name='UserField',
        ),
    ]
