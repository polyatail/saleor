from django import forms
from django.contrib.auth.models import Group
from django.utils.translation import pgettext_lazy
from django_filters import (
    CharFilter, ChoiceFilter, ModelMultipleChoiceFilter, OrderingFilter)

from ...core.filters import SortedFilterSet
from ...userprofile.models import User
from ..customer.filters import UserFilter


SORT_BY_FIELDS = (('email', 'email'),)

SORT_BY_FIELDS_LABELS = {
    'email': pgettext_lazy(
        'Customer list sorting option', 'email'),}


class StaffFilter(UserFilter):
    sort_by = OrderingFilter(
        label=pgettext_lazy('Staff list filter label', 'Sort by'),
        fields=SORT_BY_FIELDS,
        field_labels=SORT_BY_FIELDS_LABELS)

    class Meta:
        model = User
        fields = []
