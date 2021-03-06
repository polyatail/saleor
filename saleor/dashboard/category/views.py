from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import pgettext_lazy

from ...core.utils import get_paginator_items
from ...product.models import Category, UserField
from ..views import staff_member_required
from .filters import CategoryFilter
from .forms import CategoryForm, UserFieldForm


@staff_member_required
def category_list(request):
    categories = Category.tree.root_nodes().order_by('name')
    category_filter = CategoryFilter(request.GET, queryset=categories)
    categories = get_paginator_items(
        category_filter.qs, settings.DASHBOARD_PAGINATE_BY,
        request.GET.get('page'))
    ctx = {'categories': categories, 'filter': category_filter}
    return TemplateResponse(request, 'dashboard/category/list.html', ctx)


@staff_member_required
def category_create(request, root_pk=None):
    path = None
    category = Category()
    if root_pk:
        root = get_object_or_404(Category, pk=root_pk)
        path = root.get_ancestors(include_self=True) if root else []
    form = CategoryForm(request.POST or None, parent_pk=root_pk)
    if form.is_valid():
        category = form.save()
        messages.success(
            request,
            pgettext_lazy(
                'Dashboard message', 'Added category %s') % category)
        if root_pk:
            return redirect('dashboard:category-detail', pk=root_pk)
        else:
            return redirect('dashboard:category-list')
    ctx = {'category': category, 'form': form, 'path': path}
    return TemplateResponse(request, 'dashboard/category/form.html', ctx)


@staff_member_required
def category_edit(request, root_pk=None):
    path = None
    category = get_object_or_404(Category, pk=root_pk)
    if root_pk:
        root = get_object_or_404(Category, pk=root_pk)
        path = root.get_ancestors(include_self=True) if root else []
    form = CategoryForm(request.POST or None, instance=category,
                        parent_pk=category.parent_id)
    status = 200
    if form.is_valid():
        category = form.save()
        messages.success(
            request,
            pgettext_lazy(
                'Dashboard message', 'Updated category %s') % category)
        if root_pk:
            return redirect('dashboard:category-detail', pk=root_pk)
        else:
            return redirect('dashboard:category-list')
    elif form.errors:
        status = 400
    ctx = {'category': category, 'form': form, 'status': status, 'path': path}
    template = 'dashboard/category/form.html'
    return TemplateResponse(request, template, ctx, status=status)


@staff_member_required
def category_detail(request, pk):
    root = get_object_or_404(Category, pk=pk)
    path = root.get_ancestors(include_self=True) if root else []
    categories = root.get_children().order_by('name')
    category_filter = CategoryFilter(request.GET, queryset=categories)
    categories = get_paginator_items(
        category_filter.qs, settings.DASHBOARD_PAGINATE_BY,
        request.GET.get('page'))
    userfields = UserField.objects.filter(company_id=pk)

    ctx = {'categories': categories, 'path': path, 'root': root,
           'filter': category_filter, 'userfields': userfields}
    return TemplateResponse(request, 'dashboard/category/detail.html', ctx)


@staff_member_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(
            request,
            pgettext_lazy(
                'Dashboard message', 'Removed category %s') % category)
        root_pk = None
        if category.parent:
            root_pk = category.parent.pk
        if root_pk:
            if request.is_ajax():
                response = {'redirectUrl': reverse(
                    'dashboard:category-detail', kwargs={'pk': root_pk})}
                return JsonResponse(response)
            return redirect('dashboard:category-detail', pk=root_pk)
        else:
            if request.is_ajax():
                response = {'redirectUrl': reverse('dashboard:category-list')}
                return JsonResponse(response)
            return redirect('dashboard:category-list')
    ctx = {'category': category,
           'descendants': list(category.get_descendants()),
           'products_count': len(category.products.all())}
    return TemplateResponse(
        request, 'dashboard/category/modal/confirm_delete.html', ctx)

@staff_member_required
def userfield_edit(request, company_pk, userfield_pk=None):
    root = get_object_or_404(Category, pk=company_pk)
    path = root.get_ancestors(include_self=True) if root else []

    if userfield_pk: 
        userfield = get_object_or_404(UserField, pk=userfield_pk)
    else:
        userfield = UserField()
    form = UserFieldForm(request.POST or None, instance=userfield)
    form.instance.company_id = company_pk

    if form.is_valid():
        userfield = form.save()
        msg = pgettext_lazy(
            'Dashboard message', 'Updated company-specific field') if userfield_pk else pgettext_lazy(
                'Dashboard message', 'Added company-specific field')
        messages.success(request, msg)
        return redirect('dashboard:category-detail', pk=company_pk)
    ctx = {'userfield': userfield, 'form': form, 'company_pk': company_pk, 'root': root, 'path': path}
    return TemplateResponse(
        request,
        'dashboard/category/userfield_form.html',
        ctx)


@staff_member_required
def userfield_delete(request, company_pk, userfield_pk):
    userfield = get_object_or_404(UserField, pk=userfield_pk)
    if request.method == 'POST':
        userfield.delete()
        messages.success(
            request,
            pgettext_lazy(
                'Dashboard message', 'Removed company-specific field %s') % userfield.name)
        if request.is_ajax():
            response = {'redirectUrl': reverse(
                'dashboard:category-detail', kwargs={'pk': company_pk})}
            return JsonResponse(response)
        return redirect('dashboard:category-detail', pk=company_pk)
    ctx = {'userfield': userfield, 'company_pk': company_pk}
    return TemplateResponse(
        request, 'dashboard/category/modal/userfield_confirm_delete.html', ctx)
    pass



