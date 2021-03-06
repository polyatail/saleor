# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-02-02 02:59
from __future__ import unicode_literals

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import satchless.item


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('product', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('new', 'Processing'), ('cancelled', 'Cancelled'), ('shipped', 'Shipped')], default='new', max_length=32, verbose_name='order status')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('last_status_change', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='last status change')),
                ('token', models.CharField(max_length=36, unique=True, verbose_name='token')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'ordering': ('-last_status_change',),
            },
            bases=(models.Model, satchless.item.ItemSet),
        ),
        migrations.CreateModel(
            name='OrderHistoryEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='last history change')),
                ('status', models.CharField(choices=[('new', 'Processing'), ('cancelled', 'Cancelled'), ('shipped', 'Shipped')], max_length=32, verbose_name='order status')),
                ('comment', models.CharField(blank=True, default='', max_length=1000, verbose_name='comment')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history', to='order.Order', verbose_name='order')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'ordering': ('date',),
            },
        ),
        migrations.CreateModel(
            name='OrderLine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=128, verbose_name='product name')),
                ('product_sku', models.CharField(max_length=32, verbose_name='sku')),
                ('quantity', models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(999)], verbose_name='quantity')),
                ('order', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, to='order.Order')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='product.Product', verbose_name='product')),
            ],
            bases=(models.Model, satchless.item.ItemLine),
        ),
        migrations.CreateModel(
            name='OrderNote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('content', models.CharField(max_length=250, verbose_name='content')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notes', to='order.Order')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OrderUserFieldEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.CharField(default='', max_length=128, verbose_name='Submitted Data')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='userfields', to='order.Order')),
                ('userfield', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.UserField')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='orderuserfieldentry',
            unique_together=set([('order', 'userfield')]),
        ),
    ]
