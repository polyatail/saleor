from django.utils.translation import pgettext_lazy
from django_filters import CharFilter, OrderingFilter

from ...core.filters import SortedFilterSet
from ...product.models import Category

SORT_BY_FIELDS = {
    'name': pgettext_lazy('Category list sorting option', 'name'),
    'description': pgettext_lazy(
        'Category list sorting option', 'description'),}


class CategoryFilter(SortedFilterSet):
    name = CharFilter(
        label=pgettext_lazy('Category list filter label', 'Name'),
        lookup_expr='icontains')
    sort_by = OrderingFilter(
        label=pgettext_lazy('Category list sorting filter label', 'Sort by'),
        fields=SORT_BY_FIELDS.keys(),
        field_labels=SORT_BY_FIELDS)

    class Meta:
        model = Category
        fields = []
