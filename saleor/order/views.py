import logging

from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from .models import Order

logger = logging.getLogger(__name__)


def details(request, token):
    orders = Order.objects.prefetch_related('groups__lines__product')
    order = get_object_or_404(orders, token=token)
    return TemplateResponse(request, 'order/details.html',
                            {'order': order})


def confirmation(request, token):
    order = Order.objects.filter(token=token)[0]
    form_data = request.POST or None
    return TemplateResponse(request, 'order/confirmation.html',
                            {'order': order})


