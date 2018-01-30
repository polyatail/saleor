import datetime
import json

from django.conf import settings
from django.http import HttpResponsePermanentRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from ..cart.forms import UpdateUserFields
from ..cart.models import CartUserFieldEntry
from ..order.models import OrderUserFieldEntry
from ..cart.utils import set_cart_cookie
from ..core.utils import get_paginator_items, serialize_decimal
from ..core.utils.filters import get_now_sorted_by, get_sort_by_choices
from .filters import ProductFilter, SORT_BY_FIELDS
from .models import Category, AttributeChoiceValue, ProductAttribute, ProductVariant, UserField
from .utils import (
    get_availability, get_product_attributes_data, get_product_images,
    get_variant_picker_data, handle_cart_form, product_json_ld,
    products_for_cart, products_with_availability, products_with_details,
    get_or_create_user_cart)

@login_required
def product_details(request, slug, product_id, form=None):
    """Product details page

    The following variables are available to the template:

    product:
        The Product instance itself.

    is_visible:
        Whether the product is visible to regular users (for cases when an
        admin is previewing a product before publishing).

    form:
        The add-to-cart form.

    """
    products = products_with_details(user=request.user)
    product = get_object_or_404(products, id=product_id)

    # if not allowed to access this item, redirect to user's home page
    if request.user.company.id not in product.categories.values_list("id")[0]:
      return redirect('product:category', permanent=True, path=request.user.company.get_full_path(),
                      category_id=request.user.company.id)

    if product.get_slug() != slug:
        return HttpResponsePermanentRedirect(product.get_absolute_url())
    today = datetime.date.today()
    is_visible = True
    if form is None:
        form = handle_cart_form(request, product, create_cart=False)[0]
    availability = get_availability(product)
    product_images = get_product_images(product)
    variant_picker_data = get_variant_picker_data(product)
    product_attributes = get_product_attributes_data(product)
    show_variant_picker = all([v.attributes for v in product.variants.all()])
#    show_variant_picker = [v.attributes for v in product.variants.all()]
#    show_variant_picker = True if all(show_variant_picker) and show_variant_picker else False
    json_ld_data = product_json_ld(product, availability, product_attributes)

#    # figure out the appropriate variant image
#    variant_finder = {}
#
#    for k, v in request.GET.items():
#      k_id = get_object_or_404(ProductAttribute, slug=k).id
#      v_id = get_object_or_404(AttributeChoiceValue, attribute_id=k_id, slug=v).id
#
#      variant_finder["attributes__%d" % k_id] = v_id
#
#    picked_variant = ProductVariant.objects.filter(**variant_finder).first()
#
#    # try to match this variant's images to the product_images
#    for pi_idx in range(len(product_images)):
#      if product_images[pi_idx] == picked_variant.images.first():
#        product_images[pi_idx].active = True
#        break
#    else:
#      product_images[0].active = True

    if product_images:
      product_images[0].active = True

    return ({'is_visible': is_visible,
           'form': form,
           'availability': availability,
           'product': product,
           'slug': product.get_slug(),
           'image_count': range(len(product_images)),
           'product_attributes': product_attributes,
           'product_images': product_images,
           'show_variant_picker': show_variant_picker,
           'variant_picker_data': json.dumps(
               variant_picker_data, default=serialize_decimal),
           'json_ld_product_data': json.dumps(
               json_ld_data, default=serialize_decimal)})

@login_required
def product_add_to_cart(request, slug, product_id):
    # types: (int, str, dict) -> None

    if not request.method == 'POST':
        return redirect(reverse('category:index'))

    products = products_for_cart(user=request.user)
    product = get_object_or_404(products, pk=product_id)
    form, cart = handle_cart_form(request, product, create_cart=True)

    if form.is_valid():
        form.save()
        if request.is_ajax():
            response = JsonResponse({'next': reverse('cart:index')}, status=200)
        else:
            response = redirect('cart:index')
    else:
        if request.is_ajax():
            response = JsonResponse({'error': form.errors}, status=400)
        else:
            response = product_details(request, slug, product_id, form)

    return response

@login_required
def category_index(request, path, category_id):
    category_id = request.user.company.id

    category = get_object_or_404(Category, id=category_id)
    actual_path = category.get_full_path()
    if actual_path != path:
        return redirect('product:category', permanent=True, path=actual_path,
                        category_id=category_id)
    products = (products_with_details(user=request.user)
                .filter(categories__id=category.id, is_published=True)
                .order_by('name'))

    cart = get_or_create_user_cart(request.user, request)

    userfields = UserField.objects.filter(company_id=category_id)
    uf_entries = CartUserFieldEntry.objects.filter(cart=cart)
    userfield_form = UpdateUserFields(cart=cart, userfields=userfields)
    userfield_form.load_defaults(uf_entries)


    ret_products = []

    if request.user.company.description:
      message_to_users = request.user.company.description
    else:
      message_to_users = False

    for p_num, p in enumerate(products):
      p_deets = product_details(request, p.get_slug(), p.id)
      p_deets["index"] = p_num
      ret_products.append(p_deets)

    ctx = {"category": category.name,
           "products": ret_products,
           "message_to_users": message_to_users,
           "uf_form": userfield_form,
          }

    return TemplateResponse(request, 'category/index.html', ctx)

@login_required
def update_userfields(request):
    cart = get_or_create_user(request.user, request)
    userfields = UserField.objects.filter(company_id=request.user.company.id)
    form = UpdateUserFields(request, cart=cart, userfields=userfields)

    if form.is_valid():
      form.save()

    return redirect('home', permanent=True)
