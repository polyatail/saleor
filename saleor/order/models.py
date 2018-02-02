from decimal import Decimal
from uuid import uuid4

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.timezone import now
from django.utils.translation import pgettext_lazy
from satchless.item import ItemLine, ItemSet

from . import OrderStatus
from ..product.models import Product, UserField


class Order(models.Model, ItemSet):
    status = models.CharField(
        pgettext_lazy('Order field', 'order status'),
        max_length=32, choices=OrderStatus.CHOICES, default=OrderStatus.NEW)
    created = models.DateTimeField(
        pgettext_lazy('Order field', 'created'),
        default=now, editable=False)
    last_status_change = models.DateTimeField(
        pgettext_lazy('Order field', 'last status change'),
        default=now, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, related_name='orders',
        verbose_name=pgettext_lazy('Order field', 'user'),
        on_delete=models.SET_NULL)
    token = models.CharField(
        pgettext_lazy('Order field', 'token'), max_length=36, unique=True)

    class Meta:
        ordering = ('-last_status_change',)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = str(uuid4())
        return super(Order, self).save(*args, **kwargs)

    def get_lines(self):
        return OrderLine.objects.filter(order=self.id)

    def __iter__(self):
        return iter(self.groups.all())

    def __repr__(self):
        return '<Order #%r>' % (self.id,)

    def __str__(self):
        return '#%d' % (self.id, )

    def create_history_entry(self, comment='', status=None, user=None):
        if not status:
            status = self.status
        self.history.create(status=status, comment=comment, user=user)

    def can_cancel(self):
        return self.status not in {OrderStatus.CANCELLED, OrderStatus.SHIPPED}


class OrderLine(models.Model, ItemLine):
    order = models.ForeignKey(
        Order, editable=False,
        on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(
        Product, blank=True, null=True, related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=pgettext_lazy('Ordered line field', 'product'))
    product_name = models.CharField(
        pgettext_lazy('Ordered line field', 'product name'), max_length=128)
    product_sku = models.CharField(
        pgettext_lazy('Ordered line field', 'sku'), max_length=32)
    quantity = models.IntegerField(
        pgettext_lazy('Ordered line field', 'quantity'),
        validators=[MinValueValidator(0), MaxValueValidator(999)])

    def __str__(self):
        return self.product_name

    def get_quantity(self):
        return self.quantity

class OrderHistoryEntry(models.Model):
    date = models.DateTimeField(
        pgettext_lazy('Order history entry field', 'last history change'),
        default=now, editable=False)
    order = models.ForeignKey(
        Order, related_name='history',
        verbose_name=pgettext_lazy('Order history entry field', 'order'),
        on_delete=models.CASCADE)
    status = models.CharField(
        pgettext_lazy('Order history entry field', 'order status'),
        max_length=32, choices=OrderStatus.CHOICES)
    comment = models.CharField(
        pgettext_lazy('Order history entry field', 'comment'),
        max_length=1000, default='', blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True,
        verbose_name=pgettext_lazy('Order history entry field', 'user'),
        on_delete=models.SET_NULL)

    class Meta:
        ordering = ('date', )

    def __str__(self):
        return pgettext_lazy(
            'Order history entry str',
            'OrderHistoryEntry for Order #%d') % self.order.pk

class OrderNote(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey(
        Order, related_name='notes', on_delete=models.CASCADE)
    content = models.CharField(
        pgettext_lazy('Order note model', 'content'),
        max_length=250)

    def __str__(self):
        return pgettext_lazy(
            'Order note str',
            'OrderNote for Order #%d' % self.order.pk)


class OrderUserFieldEntry(models.Model):
    order = models.ForeignKey(
        Order, related_name='userfields',
        on_delete=models.CASCADE)
    userfield = models.ForeignKey(UserField, on_delete=models.CASCADE)
    data = models.CharField("Submitted Data", max_length=128, default='')

    class Meta:
        unique_together = ('order', 'userfield')
