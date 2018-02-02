"""Cart-related views."""
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.response import TemplateResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import auth, messages

from .forms import ReplaceCartLineForm
from ..order.models import Order, OrderLine, OrderUserFieldEntry
from ..product.models import ProductVariant
from .models import Cart, CartUserFieldEntry
from .utils import get_or_empty_db_cart


@login_required
@get_or_empty_db_cart(cart_queryset=Cart.objects.for_display())
def index(request, cart):
    """Display cart details."""
    cart_lines = []

    # refresh required to get updated cart lines and it's quantity
    try:
        cart = Cart.objects.get(pk=cart.pk)
    except Cart.DoesNotExist:
        pass

    for line in cart.lines.all():
        initial = {'quantity': line.get_quantity()}
        form = ReplaceCartLineForm(None, cart=cart, variant=line.variant,
                                   initial=initial)
        cart_lines.append({
            'variant': line.variant,
            'form': form})

    ctx = {
        'quantity': cart.quantity,
        'cart_lines': cart_lines,
          }

    return TemplateResponse(
        request, 'cart/index.html', ctx)


@login_required
@get_or_empty_db_cart()
def update(request, cart, variant_id):
    """Update the line quantities."""
    if not request.is_ajax():
        return redirect('cart:index')
    variant = get_object_or_404(ProductVariant, pk=variant_id)
    status = None
    form = ReplaceCartLineForm(
        request.POST, cart=cart, variant=variant)
    if form.is_valid():
        form.save()
        response = {
            'variantId': variant_id,
            'cart': {
                'numItems': cart.quantity,
                'numLines': len(cart)}}
        updated_line = cart.get_line(form.cart_line.variant)
        status = 200
    elif request.POST is not None:
        response = {'error': form.errors}
        status = 400
    return JsonResponse(response, status=status)


@login_required
@get_or_empty_db_cart(cart_queryset=Cart.objects.for_display())
def summary(request, cart):
    """Display a cart summary suitable for displaying on all pages."""
    def prepare_line_data(line):
        product_class = line.variant.product.product_class
        attributes = product_class.variant_attributes.all()
        first_image = line.variant.get_first_image()
        return {
            'product': line.variant.product,
            'variant': line.variant.name,
            'quantity': line.quantity,
            'attributes': line.variant.display_variant(attributes),
            'image': first_image,
            'update_url': reverse(
                'cart:update-line', kwargs={'variant_id': line.variant_id}),}
    if cart.quantity == 0:
        data = {'quantity': 0}
    else:
        data = {
            'quantity': cart.quantity,
            'lines': [prepare_line_data(line) for line in cart.lines.all()]}

    return render(request, 'cart-dropdown.html', data)

@login_required
@get_or_empty_db_cart(cart_queryset=Cart.objects.for_display())
def checkout(request, cart):
    # make sure this cart hasn't already been submit
    if Order.objects.filter(token=cart.token):
        raise ValueError("Cart has already been submit")

    order_data = {'user': request.user,
                  'token': cart.token}

    order = Order.objects.create(**order_data)

    # iterate through all the items in the cart and create order lines
    for l in cart.lines.all():
        ol_data = {'product_name': l.variant.product.name,
                   'product_sku': l.variant.sku,
                   'quantity': l.quantity,
                   'product_id': l.variant.product.id,
                   'order_id': order.id}

        ol = OrderLine.objects.create(**ol_data)

    # iterate through all cart userfields and create order userfields
    for c_ufe in CartUserFieldEntry.objects.filter(cart=cart):
        o_ufe_data = {'order': order,
                      'userfield': c_ufe.userfield,
                      'data': c_ufe.data}

        o_ufe = OrderUserFieldEntry.objects.create(**o_ufe_data)

    # log the user out and display a confirmation page
    auth.logout(request)
    messages.success(request, ('Your order has been successfully placed!\n\nYour order number is %s.' % (order.id,)))
    return redirect(settings.LOGIN_REDIRECT_URL)
