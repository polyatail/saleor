from django import forms
from django.utils.translation import pgettext_lazy
from django_filters import (
    CharFilter, ChoiceFilter, ModelMultipleChoiceFilter, RangeFilter,
    OrderingFilter)

from ...core.filters import SortedFilterSet
from ...product.models import (
    Category, Product, ProductAttribute, ProductClass)

PRODUCT_SORT_BY_FIELDS = {
    'name': pgettext_lazy('Product list sorting option', 'name'),
    'product_class': 'Type'}

PRODUCT_ATTRIBUTE_SORT_BY_FIELDS = {
    'name': pgettext_lazy('Product attribute list sorting option', 'name')}

PRODUCT_CLASS_SORT_BY_FIELDS = {
    'name': pgettext_lazy('Product type list sorting option', 'name')}

PUBLISHED_CHOICES = (
    ('1', pgettext_lazy('Is publish filter choice', 'Published')),
    ('0', pgettext_lazy('Is publish filter choice', 'Not published')))

FEATURED_CHOICES = (
    ('1', pgettext_lazy('Is featured filter choice', 'Featured')),
    ('0', pgettext_lazy('Is featured filter choice', 'Not featured')))


class ProductFilter(SortedFilterSet):
    name = CharFilter(
        label=pgettext_lazy('Product list filter label', 'Name'),
        lookup_expr='icontains')
    categories = ModelMultipleChoiceFilter(
        label=pgettext_lazy('Product list filter label', 'Company'),
        name='categories',
        queryset=Category.objects.all())
    is_published = ChoiceFilter(
        label=pgettext_lazy('Product list filter label', 'Is published'),
        choices=PUBLISHED_CHOICES,
        empty_label=pgettext_lazy('Filter empty choice label', 'All'),
        widget=forms.Select)
    sort_by = OrderingFilter(
        label=pgettext_lazy('Product list filter label', 'Sort by'),
        fields=PRODUCT_SORT_BY_FIELDS.keys(),
        field_labels=PRODUCT_SORT_BY_FIELDS)

    class Meta:
        model = Product
        fields = []


class ProductAttributeFilter(SortedFilterSet):
    name = CharFilter(
        label=pgettext_lazy('Product attribute list filter label', 'Name'),
        lookup_expr='icontains')
    sort_by = OrderingFilter(
        label=pgettext_lazy('Product attribute list filter label', 'Sort by'),
        fields=PRODUCT_CLASS_SORT_BY_FIELDS.keys(),
        field_labels=PRODUCT_CLASS_SORT_BY_FIELDS)

    class Meta:
        model = ProductAttribute
        fields = []


class ProductClassFilter(SortedFilterSet):
    name = CharFilter(
        label=pgettext_lazy('Product type list filter label', 'Name'),
        lookup_expr='icontains')
    sort_by = OrderingFilter(
        label=pgettext_lazy('Product class list filter label', 'Sort by'),
        fields=PRODUCT_CLASS_SORT_BY_FIELDS.keys(),
        field_labels=PRODUCT_CLASS_SORT_BY_FIELDS)

    class Meta:
        model = ProductClass
        fields = ['name', 'product_attributes', 'variant_attributes']


