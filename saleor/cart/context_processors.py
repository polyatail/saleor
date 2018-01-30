"""Cart-related context processors."""
from .utils import get_or_create_user_cart


def cart_counter(request):
    """Expose the number of items in cart."""

    # the first time this is called (upon login) it will create the session's cart
    cart = get_or_create_user_cart(request.user, request)

    if not cart:
      return {'cart_counter': 0}

    return {'cart_counter': cart.quantity}
