"""Cart-related utility functions."""
from datetime import timedelta
from functools import wraps
from uuid import UUID

from django.contrib import messages
from django.db import transaction
from django.utils.timezone import now
from django.utils.translation import pgettext_lazy

from . import CartStatus
from .models import Cart


def set_cart_cookie(simple_cart, response):
    """Update respons with a cart token cookie."""
    # FIXME: document why session is not used
    ten_years = timedelta(days=(365 * 10))
    response.set_signed_cookie(
        COOKIE_NAME, simple_cart.token, max_age=int(ten_years.total_seconds()))


def contains_unavailable_variants(cart):
    """Return `True` if cart contains any unfulfillable lines."""
    try:
        for line in cart.lines.all():
            line.variant.check_quantity(line.quantity)
    except InsufficientStock:
        return True
    return False


def token_is_valid(token):
    """Validate a cart token."""
    if token is None:
        return False
    if isinstance(token, UUID):
        return True
    try:
        UUID(token)
    except ValueError:
        return False
    return True


def remove_unavailable_variants(cart):
    """Remove any unavailable items from cart."""
    for line in cart.lines.all():
        try:
            cart.add(line.variant, quantity=line.quantity, replace=True)
        except InsufficientStock as e:
            quantity = e.item.get_stock_quantity()
            cart.add(line.variant, quantity=quantity, replace=True)


def get_product_variants_and_prices(cart, product):
    """Get variants and unit prices from cart lines matching the product."""
    lines = (
        cart_line for cart_line in cart.lines.all()
        if cart_line.variant.product_id == product.id)
    for line in lines:
        for dummy_i in range(line.quantity):
            yield line.variant, line.get_price_per_item()


def get_category_variants_and_prices(cart, root_category):
    """Get variants and unit prices from cart lines matching the category.

    Product is assumed to be in the the category if it belongs to any of its
    descendant subcategories.
    """
    products = {cart_line.variant.product for cart_line in cart.lines.all()}
    matching_products = set()
    for product in products:
        for category in product.categories.all():
            is_descendant = category.is_descendant_of(
                root_category, include_self=True)
            if is_descendant:
                matching_products.add(product)
    for product in matching_products:
        for line in get_product_variants_and_prices(cart, product):
            yield line


def check_product_availability_and_warn(request, cart):
    """Warn if cart contains any lines that cannot be fulfilled."""
    if contains_unavailable_variants(cart):
        msg = pgettext_lazy(
            'Cart warning message',
            'Sorry. We don\'t have that many items in stock. '
            'Quantity was set to maximum available for now.')
        messages.warning(request, msg)
        remove_unavailable_variants(cart)


def find_and_assign_anonymous_cart(queryset=Cart.objects.all()):
    """Assign cart from cookie to request user."""
    def get_cart(view):
        @wraps(view)
        def func(request, *args, **kwargs):
            response = view(request, *args, **kwargs)
            token = request.get_signed_cookie(COOKIE_NAME, default=None)
            if not token_is_valid(token):
                return response
            cart = get_anonymous_cart_from_token(
                token=token, cart_queryset=queryset)
            if cart is None:
                return response
            if request.user.is_authenticated:
                with transaction.atomic():
                    cart.change_user(request.user)
                    carts_to_close = Cart.objects.open().filter(
                        user=request.user)
                    carts_to_close = carts_to_close.exclude(token=token)
                    carts_to_close.update(
                        status=CartStatus.CANCELED, last_status_change=now())
                response.delete_cookie(COOKIE_NAME)
            return response

        return func
    return get_cart


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
            if not request.user.is_authenticated:
                set_cart_cookie(cart, response)
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


