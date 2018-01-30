# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-30 02:18
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0004_auto_20180129_2018'),
        ('order', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderUserFieldEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.CharField(max_length=128, verbose_name='Submitted Data')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='userfields', to='order.Order')),
                ('userfield', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.UserField')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='orderuserfieldentry',
            unique_together=set([('order', 'userfield', 'data')]),
        ),
    ]
