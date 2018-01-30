"""Cart-related utility functions."""
from functools import wraps

from django.utils.translation import pgettext_lazy

from .models import Cart


def get_product_variants_and_prices(cart, product):
    """Get variants and unit prices from cart lines matching the product."""
    lines = (
        cart_line for cart_line in cart.lines.all()
        if cart_line.variant.product_id == product.id)
    for line in lines:
        for dummy_i in range(line.quantity):
            yield line.variant, line.get_price_per_item()


def get_or_create_user_cart(user, request, cart_queryset=Cart.objects.all()):
    """Return an open cart for given user or create a new one."""
    if not user.is_authenticated():
      return None

    return cart_queryset.open().get_or_create(user=user, token=request.session.session_key)[0]


def get_user_cart(user, request, cart_queryset=Cart.objects.all()):
    """Return an open cart for given user if any.""" 
    if not user.is_authenticated():
      return None

    return cart_queryset.open().filter(user=user, token=request.session.session_key).first()


def get_or_create_db_cart(cart_queryset=Cart.objects.all()):
    """Decorate view to always receive a saved cart instance.

    Changes the view signature from `fund(request, ...)` to
    `func(request, cart, ...)`.

    If no matching cart is found, one will be created and a cookie will be set
    for users who are not logged in.
    """
    # FIXME: behave like middleware and assign cart to request instead
    def get_cart(view):
        @wraps(view)
        def func(request, *args, **kwargs):
            cart = get_or_create_user_cart(request.user, request, cart_queryset)
            response = view(request, cart, *args, **kwargs)
            return response
        return func
    return get_cart


def get_or_empty_db_cart(cart_queryset=Cart.objects.all()):
    """Decorate view to receive a cart if one exists.

    Changes the view signature from `fund(request, ...)` to
    `func(request, cart, ...)`.

    If no matching cart is found, an unsaved `Cart` instance will be used.
    """
    # FIXME: behave like middleware and assign cart to request instead
    def get_cart(view):
        @wraps(view)
        def func(request, *args, **kwargs):
            cart = get_user_cart(request.user, request, cart_queryset)
            return view(request, cart, *args, **kwargs)
        return func
    return get_cart


