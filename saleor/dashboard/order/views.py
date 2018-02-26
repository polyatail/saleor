from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.context_processors import csrf
from django.template.response import TemplateResponse
from django.utils.translation import pgettext_lazy
from django.utils.text import slugify

from .filters import OrderFilter
from .forms import (
    CancelLinesForm,
    CancelOrderForm, ChangeQuantityForm,
    OrderNoteForm)

from ..views import staff_member_required
from ...core.utils import get_paginator_items
from ...order import OrderStatus
from ...order.models import Order, OrderLine, OrderNote, OrderUserFieldEntry
from ...product.models import Product, UserField, Category

import csv


@staff_member_required
def order_list(request):
    orders = (Order.objects.prefetch_related('user').order_by('-pk'))
    order_filter = OrderFilter(request.GET, queryset=orders)
    orders = get_paginator_items(
        order_filter.qs, settings.DASHBOARD_PAGINATE_BY,
        request.GET.get('page'))
    ctx = {'orders': orders, 'filter': order_filter}
    return TemplateResponse(request, 'dashboard/order/list.html', ctx)


@staff_member_required
def order_export_list(request):
    ctx = {'companies': Category.objects.all()}
    return TemplateResponse(request, 'dashboard/order/export_list.html', ctx)

 
@staff_member_required
def order_export(request, company_id):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="%s_export.csv"' % \
        (slugify(get_object_or_404(Category.objects.all(), id=company_id)))

    # get all skus in this company
    skus = []

    for p in Product.objects.all().filter(categories__id=company_id):
      for v in p.variants.all():
        skus.append(v.sku)

    # get all userfields in this company
    userfields = []

    for uf in UserField.objects.all().filter(company__id=company_id):
      userfields.append(uf.name)

    outfile = []

    # build the header
    header = ["Order ID", "Date", "Status"] + userfields + skus

    # entries to index dictionary
    entry_to_idx = dict([(y, x) for x, y in enumerate(header)])

    # iterate through all orders in this company
    for o in Order.objects.all().filter(user__company__id=company_id):
      my_line = [o.id, o.created, o.status] + ([""] * len(userfields)) + ([0] * len(skus))

      # insert quantities into line
      for ol in o.get_lines():
        # if this SKU was deleted at some point, manually add a column for it
        try:
          my_line[entry_to_idx[ol.product_sku]] = ol.quantity
        except KeyError:
          header.append(ol.product_sku)
          entry_to_idx = dict([(y, x) for x, y in enumerate(header)])

        my_line[entry_to_idx[ol.product_sku]] = ol.quantity

      # insert userfields into line
      for uf in o.get_userfields():
        my_line[entry_to_idx[uf.userfield.name]] = uf.data

      outfile.append(my_line)

    # prepend the header on to the output list
    outfile.insert(0, header)

    # then write the contents
    writer = csv.writer(response)

    for line in outfile:
      writer.writerow(line)

    return response

@staff_member_required
def order_details(request, order_pk):
    qs = (Order.objects
          .select_related('user',)
          .prefetch_related('notes', 'history'))
    order = get_object_or_404(qs, pk=order_pk)
    notes = order.notes.all()
    lines = order.get_lines()

    ufes = OrderUserFieldEntry.objects.filter(order=order)

    ctx = {'order': order, 'lines': lines, 'notes': notes, 'userfields': ufes}
    return TemplateResponse(request, 'dashboard/order/detail.html', ctx)


@staff_member_required
def order_add_note(request, order_pk):
    order = get_object_or_404(Order, pk=order_pk)
    note = OrderNote(order=order, user=request.user)
    form = OrderNoteForm(request.POST or None, instance=note)
    status = 200
    if form.is_valid():
        form.save()
        msg = pgettext_lazy(
            'Dashboard message related to an order',
            'Added note')
        order.create_history_entry(comment=msg, user=request.user)
        messages.success(request, msg)
    elif form.errors:
        status = 400
    ctx = {'order': order, 'form': form}
    ctx.update(csrf(request))
    template = 'dashboard/order/modal/add_note.html'
    return TemplateResponse(request, template, ctx, status=status)


@staff_member_required
def orderline_change_quantity(request, order_pk, line_pk):
    order = get_object_or_404(Order, pk=order_pk)
    line = get_object_or_404(OrderLine, pk=line_pk)
    form = ChangeQuantityForm(request.POST or None, instance=line)
    status = 200
    old_quantity = line.quantity
    if form.is_valid():
        msg = pgettext_lazy(
            'Dashboard message related to an order line',
            'Changed quantity for product %(product)s from'
            ' %(old_quantity)s to %(new_quantity)s') % {
                'product': line.product, 'old_quantity': old_quantity,
                'new_quantity': line.quantity}
        with transaction.atomic():
            order.create_history_entry(comment=msg, user=request.user)
            form.save()
            messages.success(request, msg)
        return redirect('dashboard:order-details', order_pk=order.pk)
    elif form.errors:
        status = 400
    ctx = {'order': order, 'object': line, 'form': form}
    template = 'dashboard/order/modal/change_quantity.html'
    return TemplateResponse(request, template, ctx, status=status)


@staff_member_required
def orderline_cancel(request, order_pk, line_pk):
    order = get_object_or_404(Order, pk=order_pk)
    line = get_object_or_404(OrderLine, pk=line_pk)
    form = CancelLinesForm(data=request.POST or None, line=line)
    status = 200

    if form.is_valid():
        msg = pgettext_lazy(
            'Dashboard message related to an order line',
            'Cancelled item %s') % line
        with transaction.atomic():
            order.create_history_entry(comment=msg, user=request.user)
            form.cancel_line()
            messages.success(request, msg)
        return redirect('dashboard:order-details', order_pk=order.pk)
    elif form.errors:
        status = 400
    ctx = {'order': order, 'item': line, 'form': form}
    return TemplateResponse(
        request, 'dashboard/order/modal/cancel_line.html',
        ctx, status=status)


@staff_member_required
def cancel_order(request, order_pk):
    status = 200
    order = get_object_or_404(Order, pk=order_pk)
    form = CancelOrderForm(request.POST or None, order=order)
    if form.is_valid():
        msg = pgettext_lazy('Dashboard message', 'Cancelled order')
        with transaction.atomic():
            form.cancel_order()
            order.create_history_entry(comment=msg, user=request.user)
        messages.success(request, 'Order cancelled')
        return redirect('dashboard:order-details', order_pk=order.pk)
        # TODO: send status confirmation email
    elif form.errors:
        status = 400
    ctx = {'order': order}
    return TemplateResponse(request, 'dashboard/order/modal/cancel_order.html',
                            ctx, status=status)


@staff_member_required
def ship_order(request, order_pk):
    status = 200
    order = get_object_or_404(Order, pk=order_pk)
    order.status = OrderStatus.SHIPPED
    order.save()
    msg = pgettext_lazy('Dashboard message', 'Order marked as shipped')
    with transaction.atomic():
        order.create_history_entry(comment=msg, user=request.user)
    messages.success(request, 'Order marked as shipped')
    return redirect('dashboard:order-details', order_pk=order.pk)

