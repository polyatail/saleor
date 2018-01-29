from django import forms
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse_lazy
from django.utils.translation import npgettext_lazy, pgettext_lazy

from ...cart.forms import QuantityField
from ...core.forms import AjaxSelect2ChoiceField
from ...order import OrderStatus
from ...order.models import OrderLine, OrderNote
from ...order.utils import (
    cancel_order,
    change_order_line_quantity, merge_duplicates_into_order_line,
    recalculate_order, remove_empty_groups
)
from ...product.models import Product, ProductVariant


class OrderNoteForm(forms.ModelForm):
    class Meta:
        model = OrderNote
        fields = ['content']
        widgets = {
            'content': forms.Textarea()
        }

    def __init__(self, *args, **kwargs):
        super(OrderNoteForm, self).__init__(*args, **kwargs)


class CancelLinesForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.line = kwargs.pop('line')
        super(CancelLinesForm, self).__init__(*args, **kwargs)

    def cancel_line(self):
        order = self.line.order
        self.line.quantity = 0
        remove_empty_groups(self.line)


class ChangeQuantityForm(forms.ModelForm):
    quantity = QuantityField(
        label=pgettext_lazy('Change quantity form label', 'Quantity'),
        validators=[MinValueValidator(1)])

    class Meta:
        model = OrderLine
        fields = ['quantity']

    def __init__(self, *args, **kwargs):
        super(ChangeQuantityForm, self).__init__(*args, **kwargs)
        self.initial_quantity = self.instance.quantity
        self.fields['quantity'].initial = self.initial_quantity

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        delta = quantity - self.initial_quantity
        return quantity

    def save(self):
        quantity = self.cleaned_data['quantity']
        change_order_line_quantity(self.instance, quantity)
        return self.instance


class CancelOrderForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.order = kwargs.pop('order')
        super(CancelOrderForm, self).__init__(*args, **kwargs)

    def clean(self):
        data = super(CancelOrderForm, self).clean()
        if not self.order.can_cancel():
            raise forms.ValidationError(
                pgettext_lazy(
                    'Cancel order form error',
                    'This order can\'t be cancelled'))
        return data

    def cancel_order(self):
        cancel_order(self.order)


ORDER_STATUS_CHOICES = [
    ('', pgettext_lazy('Order status field value', 'All'))
] + OrderStatus.CHOICES


