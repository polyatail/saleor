from functools import wraps

from django.conf import settings
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import pgettext_lazy
from prices import Price
from satchless.item import InsufficientStock

from ..product.models import Stock
from ..userprofile.utils import store_user_address
from .models import Order, OrderLine
from . import OrderStatus


def check_order_status(func):
    """Preserves execution of function if order is fully paid by redirecting
    to order's details page."""
    @wraps(func)
    def decorator(*args, **kwargs):
        token = kwargs.pop('token')
        order = get_object_or_404(Order, token=token)
        if order.is_fully_paid():
            return redirect('order:details', token=order.token)
        kwargs['order'] = order
        return func(*args, **kwargs)

    return decorator


def cancel_order(order):
    """Cancells order by cancelling all associated shipment groups."""
    order.status = OrderStatus.CANCELLED
    order.save()


def recalculate_order(order):
    """Recalculates and assigns total price of order.
    Total price is a sum of items and shippings in order shipment groups. """
    order.total = 0
    order.save()


def attach_order_to_user(order, user):
    """Associates existing order with user account."""
    order.user = user
    store_user_address(user, order.billing_address, billing=True)
    if order.shipping_address:
        store_user_address(user, order.shipping_address, shipping=True)
    order.save(update_fields=['user'])


def fill_group_with_partition(group, partition, discounts=None):
    """Fills shipment group with order lines created from partition items.
    """
    for item in partition:
        add_variant_to_delivery_group(
            group, item.variant, item.get_quantity(), discounts,
            add_to_existing=False)


def add_variant_to_delivery_group(
        group, variant, total_quantity, discounts=None, add_to_existing=True):
    """Adds total_quantity of variant to group.
    Raises InsufficientStock exception if quantity could not be fulfilled.

    By default, first adds variant to existing lines with same variant.
    It can be disabled with setting add_to_existing to False.

    Order lines are created by increasing quantity of lines,
    as long as total_quantity of variant will be added.
    """
    group.lines.create(
        product=variant.product,
        product_name=variant.display_product(),
        product_sku=variant.sku,
        quantity=total_quantity)


def add_variant_to_existing_lines(group, variant, total_quantity):
    """Adds variant to existing lines with same variant.

    Variant is added by increasing quantity of lines with same variant,
    as long as total_quantity of variant will be added
    or there is no more lines with same variant.

    Returns quantity that could not be fulfilled with existing lines.
    """
    # order descending by lines' stock available quantity
    lines = group.lines.filter(
        product=variant.product, product_sku=variant.sku,
        stock__isnull=False).order_by(
            F('stock__quantity_allocated') - F('stock__quantity'))

    quantity_left = total_quantity
    for line in lines:
        quantity = (
            line.stock.quantity_available
            if quantity_left > line.stock.quantity_available
            else quantity_left)
        line.quantity += quantity
        line.save()
        Stock.objects.allocate_stock(line.stock, quantity)
        quantity_left -= quantity
        if quantity_left == 0:
            break
    return quantity_left


def cancel_delivery_group(group, cancel_order=True):
    """Cancells shipment group and (optionally) it's order if necessary."""
    for line in group:
        if line.stock:
            Stock.objects.deallocate_stock(line.stock, line.quantity)
    group.status = OrderStatus.CANCELLED
    group.save()
    if cancel_order:
        other_groups = group.order.groups.all()
        statuses = set(other_groups.values_list('status', flat=True))
        if statuses == {OrderStatus.CANCELLED}:
            # Cancel whole order
            group.order.status = OrderStatus.CANCELLED
            group.order.save(update_fields=['status'])


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


