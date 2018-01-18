"""Checkout session state management."""
from datetime import date
from functools import wraps

from django.conf import settings
from django.db import transaction
from django.forms.models import model_to_dict
from django.utils.encoding import smart_text
from django.utils.translation import get_language
from prices import FixedDiscount, Price

from ..cart.models import Cart
from ..cart.utils import get_or_empty_db_cart
from ..core import analytics
from ..order.models import Order, OrderLine
from ..order.utils import fill_group_with_partition
from ..shipping.models import ANY_COUNTRY, ShippingMethodCountry
from ..userprofile.models import Address
from ..userprofile.utils import store_user_address

from phonenumber_field.phonenumber import PhoneNumber

STORAGE_SESSION_KEY = 'checkout_storage'


class Checkout:
    """Represents a checkout session.

    This object acts a temporary storage for the entire checkout session. An
    order instance is only created when the user confirms their order and is
    ready to pay.

    `VERSION` is used to prevent code trying to work with incompatible
    checkout structures.

    The `modified` attribute keeps track of when checkout state changes and
    needs to be saved.
    """

    VERSION = '1.0.0'

    def __init__(self, cart, user, tracking_code):
        self.modified = False
        self.cart = cart
        self.storage = {'version': self.VERSION}
        self.tracking_code = tracking_code
        self.user = user

    @classmethod
    def from_storage(cls, storage_data, cart, user, tracking_code):
        """Restore a previously serialized checkout session.

        `storage_data` is the value previously returned by
        `Checkout.for_storage()`.
        """
        checkout = cls(cart, user, tracking_code)
        checkout.storage = storage_data
        try:
            version = checkout.storage['version']
        except (TypeError, KeyError):
            version = None
        if version != cls.VERSION:
            checkout.storage = {'version': cls.VERSION}
        return checkout

    def for_storage(self):
        """Serialize a checkout session to allow persistence.

        The session can later be restored using `Checkout.from_storage()`.
        """
        return self.storage

    def clear_storage(self):
        """Discard the entire state."""
        self.storage = None
        self.modified = True

    @property
    def email(self):
        """Return the customer email if any."""
        return self.storage.get('email')

    @email.setter
    def email(self, email):
        self.storage['email'] = email
        self.modified = True

    @property
    def employeeid(self):
        """ Custom field for Grace """
        try:
          return self.storage['employeeid']
        except KeyError:
          return None

    @employeeid.setter
    def employeeid(self, employeeid):
        self.storage['employeeid'] = employeeid

    @transaction.atomic
    def create_order(self):
        """Create an order from the checkout session.

        Each order will get a private copy of both the billing and the shipping
        address (if shipping ).

        If any of the addresses is new and the user is logged in the address
        will also get saved to that user's address book.

        Current user's language is saved in the order so we can later determine
        which language to use when sending email.
        """
        order_data = {
            'language_code': get_language(),
            'tracking_client_id': self.tracking_code}

        if self.user.is_authenticated:
            order_data['user'] = self.user
            order_data['user_email'] = self.user.email
        else:
            order_data['user_email'] = self.email

        order_data['employeeid'] = self.employeeid

        order = Order.objects.create(**order_data)

        # iterate through all the items in the cart and create order lines
        for l in self.cart.lines.all():
            ol_data = {'product_name': l.variant.product.name,
                       'product_sku': l.variant.sku,
                       'quantity': l.quantity,
                       'product_id': l.variant.product.id,
                       'order_id': order.id}

            ol = OrderLine.objects.create(**ol_data)

        return order



def load_checkout(view):
    """Decorate view with checkout session and cart for each request.

    Any views decorated by this will change their signature from
    `func(request)` to `func(request, checkout, cart)`.
    """
    # FIXME: behave like middleware and assign checkout and cart to request
    # instead of changing the view signature
    @wraps(view)
    @get_or_empty_db_cart(Cart.objects.for_display())
    def func(request, cart):
        try:
            session_data = request.session[STORAGE_SESSION_KEY]
        except KeyError:
            session_data = ''
        tracking_code = analytics.get_client_id(request)
        checkout = Checkout.from_storage(
            session_data, cart, request.user, tracking_code)
        response = view(request, checkout, cart)
        if checkout.modified:
            request.session[STORAGE_SESSION_KEY] = checkout.for_storage()
        return response

    return func
