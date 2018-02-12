from collections import defaultdict, namedtuple
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.utils.encoding import smart_text

from . import ProductAvailabilityStatus, VariantAvailabilityStatus
from ..cart.utils import get_user_cart, get_or_create_user_cart
from .forms import ProductForm


def products_visible_to_user(user):
    from .models import Product
    if user.is_authenticated and user.is_active and user.is_staff:
        return Product.objects.all()
    else:
        return None


def products_with_details(user):
    products = products_visible_to_user(user)
    products = products.prefetch_related(
        'categories', 'images', 
        'variants__variant_images__image', 'attributes__values',
        'product_class__variant_attributes__values',
        'product_class__product_attributes__values')
    return products


def get_product_images(product):
    """
    Returns list of product images that will be placed in product gallery
    """
    return list(product.images.all())


def handle_cart_form(request, product, create_cart=False):
    if create_cart:
        cart = get_or_create_user_cart(request.user, request)
    else:
        cart = get_user_cart(request.user, request)
    form = ProductForm(
        cart=cart, product=product, data=request.POST or None)
    return form, cart


def products_for_cart(user):
    products = products_visible_to_user(user)
    products = products.prefetch_related('variants__variant_images__image')
    return products


def product_json_ld(product, attributes=None):
    # type: (saleor.product.models.Product, saleor.product.utils.ProductAvailability, dict) -> dict  # noqa
    """Generates JSON-LD data for product"""
    data = {'@context': 'http://schema.org/',
            '@type': 'Product',
            'name': smart_text(product),
            'image': smart_text(product.get_first_image()),
            #'description': product.description,
            'offers': {'@type': 'Offer',
                       'itemCondition': 'http://schema.org/NewCondition',
                       'availability': 'http://schema.org/InStock'}}

    if attributes is not None:
        brand = ''
        for key in attributes:
            if key.name == 'brand':
                brand = attributes[key].name
                break
            elif key.name == 'publisher':
                brand = attributes[key].name

        if brand:
            data['brand'] = {'@type': 'Thing', 'name': brand}
    return data


def get_variant_picker_data(product):
    variants = product.variants.all()
    data = {'variantAttributes': [], 'variants': []}

    variant_attributes = product.product_class.variant_attributes.all()

    # Collect only available variants
    filter_available_variants = defaultdict(list)

    for variant in variants:
        schema_data = {'@type': 'Offer',
                       'itemCondition': 'http://schema.org/NewCondition',}

        schema_data['availability'] = 'http://schema.org/InStock'

        variant_data = {
            'id': variant.id,
            'attributes': variant.attributes,
            'schemaData': schema_data}
        data['variants'].append(variant_data)

        for variant_key, variant_value in variant.attributes.items():
            filter_available_variants[int(variant_key)].append(
                int(variant_value))

    for attribute in variant_attributes:
        available_variants = filter_available_variants.get(attribute.pk, None)

        if available_variants:
            data['variantAttributes'].append({
                'pk': attribute.pk,
                'name': attribute.name,
                'slug': attribute.slug,
                'values': [
                    {'pk': value.pk, 'name': value.name, 'slug': value.slug}
                    for value in attribute.values.filter(
                        pk__in=available_variants)]})

    return data


def get_product_attributes_data(product):
    attributes = product.product_class.product_attributes.all()
    attributes_map = {attribute.pk: attribute for attribute in attributes}
    values_map = get_attributes_display_map(product, attributes)
    return {attributes_map.get(attr_pk): value_obj
            for (attr_pk, value_obj) in values_map.items()}


def get_attributes_display_map(obj, attributes):
    display_map = {}
    for attribute in attributes:
        value = obj.attributes.get(smart_text(attribute.pk))
        if value:
            choices = {smart_text(a.pk): a for a in attribute.values.all()}
            choice_obj = choices.get(value)
            if choice_obj:
                display_map[attribute.pk] = choice_obj
            else:
                display_map[attribute.pk] = value
    return display_map


