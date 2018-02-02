from django import forms
from django.db.models import Q
from django.utils.translation import pgettext_lazy
from django_filters import (
    CharFilter, ChoiceFilter, OrderingFilter)

from ...core.filters import SortedFilterSet
from ...userprofile.models import User


SORT_BY_FIELDS = (
    ('email', 'email'),)

SORT_BY_FIELDS_LABELS = {
    'email': pgettext_lazy(
        'Customer list sorting option', 'email'),}

IS_ACTIVE_CHOICES = (
    ('1', pgettext_lazy('Is active filter choice', 'Active')),
    ('0', pgettext_lazy('Is active filter choice', 'Not active')))


class UserFilter(SortedFilterSet):
    name_or_email = CharFilter(
        label="Email",
        method='filter_by_customer')
    is_active = ChoiceFilter(
        label=pgettext_lazy('Customer list filter label', 'Is active'),
        choices=IS_ACTIVE_CHOICES,
        empty_label=pgettext_lazy('Filter empty choice label', 'All'),
        widget=forms.Select)
    sort_by = OrderingFilter(
        label=pgettext_lazy('Customer list filter label', 'Sort by'),
        fields=SORT_BY_FIELDS,
        field_labels=SORT_BY_FIELDS_LABELS)

    class Meta:
        model = User
        fields = []

    def filter_by_customer(self, queryset, name, value):
        return queryset.filter(Q(email__icontains=value))


