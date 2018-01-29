from django import forms
from django.conf import settings
from django_filters.widgets import RangeWidget


class DateRangeWidget(RangeWidget):
    def __init__(self, attrs=None):
        widgets = (forms.DateInput, forms.DateInput)
        super(RangeWidget, self).__init__(widgets, attrs)


