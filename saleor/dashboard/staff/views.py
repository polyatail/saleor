from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.translation import pgettext_lazy

from .filters import StaffFilter
from .forms import StaffForm
from ..views import staff_member_required
from ...core.utils import get_paginator_items
from ...userprofile.models import User


@staff_member_required
def staff_list(request):
    staff_members = (User.objects.all()
                     .order_by('username'))
    staff_filter = StaffFilter(request.GET, queryset=staff_members)
    staff_members = get_paginator_items(
        staff_filter.qs, settings.DASHBOARD_PAGINATE_BY,
        request.GET.get('page'))
    ctx = {'staff': staff_members, 'filter': staff_filter}
    return TemplateResponse(request, 'dashboard/staff/list.html', ctx)


@staff_member_required
def staff_details(request, pk):
    queryset = User.objects.all()
    staff_member = get_object_or_404(queryset, pk=pk)
    form = StaffForm(
        request.POST or None, instance=staff_member, user=request.user)
    prior_pw = staff_member.password
    if form.is_valid():
        if form.instance.password:
          form.instance.set_password(form.instance.password)
        else:
          form.instance.password = prior_pw
        form.save()
        msg = pgettext_lazy(
            'Dashboard message', 'Updated user account %s') % staff_member
        messages.success(request, msg)
        redirect('dashboard:staff-list')
    ctx = {'staff_member': staff_member, 'form': form}
    return TemplateResponse(request, 'dashboard/staff/detail.html', ctx)


@staff_member_required
def staff_create(request):
    staff = User()
    form = StaffForm(request.POST or None, instance=staff)
    if form.is_valid():
        form.save()
        msg = pgettext_lazy(
            'Dashboard message', 'Added user account %s') % staff
        messages.success(request, msg)
        return redirect('dashboard:staff-list')
    ctx = {'form': form}
    return TemplateResponse(request, 'dashboard/staff/detail.html', ctx)


@staff_member_required
def staff_delete(request, pk):
    queryset = User.objects.prefetch_related(
        'orders')
    staff = get_object_or_404(queryset, pk=pk)
    all_orders_count = staff.orders.count()
    if request.method == 'POST':
        staff.delete()
        msg = pgettext_lazy(
            'Dashboard message', 'Removed user account %s') % staff
        messages.success(request, msg)
        return redirect('dashboard:staff-list')
    return TemplateResponse(
        request, 'dashboard/staff/modal/confirm_delete.html',
        {'staff': staff, 'orders': all_orders_count})
