from functools import wraps

from django.conf import settings
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import pgettext_lazy

from .models import Order, OrderLine
from . import OrderStatus


def cancel_order(order):
    """Cancells order by cancelling all associated shipment groups."""
    order.status = OrderStatus.CANCELLED
    order.save()


def recalculate_order(order):
    """Recalculates and assigns total price of order.
    Total price is a sum of items and shippings in order shipment groups. """
    order.total = 0
    order.save()


def merge_duplicates_into_order_line(line):
    """Merges duplicated lines in shipment group into one (given) line.
    If there are no duplicates, nothing will happen.
    """
    lines = line.delivery_group.lines.filter(
        product=line.product, product_name=line.product_name,
        product_sku=line.product_sku, stock=line.stock)
    if lines.count() > 1:
        line.quantity = sum([line.quantity for line in lines])
        line.save()
        lines.exclude(pk=line.pk).delete()


def change_order_line_quantity(line, new_quantity):
    """Change the quantity of ordered items in a order line."""
    line.quantity = new_quantity
    line.save()

    if not line.quantity:
        order = line.order
        line.delete()
        if not order.get_lines():
            order.status = OrderStatus.CANCELLED
            order.save()
            order.create_history_entry(
                status=OrderStatus.CANCELLED, comment=pgettext_lazy(
                    'Order status history entry',
                    'Order cancelled. No items in order'))


def remove_empty_groups(line):
    """Removes order line and associated shipment group and order.
    Remove is done only if quantity of order line or items in group or in order
    is equal to 0."""
    order = line.order
    if line.quantity:
        line.save()
    else:
        line.delete()

    if not order.get_lines():
        order.status = OrderStatus.CANCELLED
        order.save()
        order.create_history_entry(
            status=OrderStatus.CANCELLED, comment=pgettext_lazy(
                'Order status history entry',
                'Order cancelled. No items in order'))


