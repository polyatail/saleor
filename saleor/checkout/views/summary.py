from django.contrib import messages
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils.translation import pgettext, pgettext_lazy
from satchless.item import InsufficientStock

from ...order import OrderStatus


def create_order(checkout):
    """Finalize a checkout session and create an order.

    This is a helper function.

    `checkout` is a `saleor.checkout.core.Checkout` instance.
    """
    order = checkout.create_order()
    if not order:
        return None, redirect('checkout:summary')
    checkout.clear_storage()
    checkout.cart.clear()
    user = None if checkout.user.is_anonymous else checkout.user
    order.create_history_entry(
        status=OrderStatus.NEW, user=user, comment=pgettext_lazy(
            'Order status history entry', 'Order was placed'))
    order.send_confirmation_email()
    return order, redirect('order:confirmation', token=order.token)


def handle_order_placement(request, checkout):
    """Try to create an order and redirect the user as necessary.

    This is a helper function.
    """
    try:
        order, redirect_url = create_order(checkout)
    except InsufficientStock:
        return redirect('cart:index')
    if not order:
        msg = pgettext('Checkout warning', 'Please review your checkout.')
        messages.warning(request, msg)
    return redirect_url


def summary_no_address(request, checkout):
    if "employeeid" in request.POST:
        if request.POST["employeeid"]:
            checkout.employeeid = request.POST["employeeid"]
            return handle_order_placement(request, checkout)
        else:
            msg = pgettext('Checkout warning', 'Employee ID is a required field.')
            messages.warning(request, msg)

    return TemplateResponse(request, 'checkout/details.html',
                            context={'checkout': checkout, 'lines': [x for x in checkout.cart.lines.all()]})
