from __future__ import unicode_literals

from django_filters import (FilterSet, OrderingFilter)
from django.utils.translation import pgettext_lazy

from ...userprofile.models import User


SORT_BY_FIELDS = {
    'email': pgettext_lazy(
        'Customer list sorting option', 'email'),
    'default_billing_address__first_name': pgettext_lazy(
        'Customer list sorting option', 'name'),
    'default_billing_address__city': pgettext_lazy(
        'Customer list sorting option', 'location'),
    'num_orders': pgettext_lazy(
        'Customer list sorting option', 'number of orders'),
    'last_order': pgettext_lazy(
        'Customer list sorting option', 'last order')}


class CustomerFilter(FilterSet):
    sort_by = OrderingFilter(
        label=pgettext_lazy('Product list sorting form', 'Sort by'),
        fields=SORT_BY_FIELDS.keys(),
        field_labels=SORT_BY_FIELDS
    )

    class Meta:
        model = User
        fields = ['email', 'is_active', 'is_staff']