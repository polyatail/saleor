from decimal import Decimal
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import pgettext_lazy
from django_prices.models import PriceField
from payments import PaymentStatus, PurchasedItem
from payments.models import BasePayment
from prices import FixedDiscount, Price
from satchless.item import ItemLine, ItemSet

from . import OrderStatus, emails
from ..core.utils import build_absolute_uri
from ..discount.models import Voucher
from ..product.models import Product
from ..userprofile.models import Address


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
    language_code = models.CharField(
        max_length=35, default=settings.LANGUAGE_CODE)
    tracking_client_id = models.CharField(
        pgettext_lazy('Order field', 'tracking client id'),
        max_length=36, blank=True, editable=False)
    user_email = models.EmailField(
        pgettext_lazy('Order field', 'user email'),
        blank=True, default='', editable=False)
    token = models.CharField(
        pgettext_lazy('Order field', 'token'), max_length=36, unique=True)
    employeeid = models.CharField(
        pgettext_lazy('Order field', 'employeeid'), max_length=256)

    class Meta:
        ordering = ('-last_status_change',)
        permissions = (
            ('view_order',
             pgettext_lazy('Permission description', 'Can view orders')),
            ('edit_order',
             pgettext_lazy('Permission description', 'Can edit orders')))

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = str(uuid4())
        return super(Order, self).save(*args, **kwargs)

    def get_lines(self):
        return OrderLine.objects.filter(order=self.id)

    def get_user_current_email(self):
        return self.user.email if self.user else self.user_email

    def __iter__(self):
        return iter(self.groups.all())

    def __repr__(self):
        return '<Order #%r>' % (self.id,)

    def __str__(self):
        return '#%d' % (self.id, )

    def get_absolute_url(self):
        return reverse('order:details', kwargs={'token': self.token})

    def send_confirmation_email(self):
        email = self.get_user_current_email()
        payment_url = build_absolute_uri(
            reverse('order:details', kwargs={'token': self.token}))
        emails.send_order_confirmation.delay(email, payment_url)

    def create_history_entry(self, comment='', status=None, user=None):
        if not status:
            status = self.status
        self.history.create(status=status, comment=comment, user=user)

    def can_cancel(self):
        return self.status not in {OrderStatus.CANCELLED, OrderStatus.SHIPPED}


class OrderLine(models.Model, ItemLine):
    order = models.ForeignKey(
        Order, editable=False,
        on_delete=models.CASCADE)
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
