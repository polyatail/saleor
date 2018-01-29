import decimal
from urllib.parse import urljoin

from django import forms
from django.core.paginator import InvalidPage, Paginator
from django.http import Http404
from django.utils.encoding import iri_to_uri, smart_text
from django.conf import settings

from ...userprofile.models import User


class CategoryChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        # pylint: disable=W0212
        level = getattr(obj, obj._mptt_meta.level_attr)
        indent = max(0, level - 1) * '│'
        if obj.parent:
            last = ((obj.parent.rght - obj.rght == 1) and
                    (obj.rght - obj.lft == 1))
            if last:
                indent += '└ '
            else:
                indent += '├ '
        return '%s%s' % (indent, smart_text(obj))


def build_absolute_uri(location, is_secure=False):
    # type: (str, bool, saleor.site.models.SiteSettings) -> str
    host = settings.SITE_DOMAIN
    current_uri = '%s://%s' % ('https' if is_secure else 'http', host)
    location = urljoin(current_uri, location)
    return iri_to_uri(location)


def get_client_ip(request):
    ip = request.META.get('HTTP_X_FORWARDED_FOR', None)
    if ip:
        return ip.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', None)


def get_paginator_items(items, paginate_by, page_number):
    if not page_number:
        page_number = 1
    paginator = Paginator(items, paginate_by)
    try:
        page_number = int(page_number)
    except ValueError:
        raise Http404('Page can not be converted to an int.')

    try:
        items = paginator.page(page_number)
    except InvalidPage as err:
        raise Http404('Invalid page (%(page_number)s): %(message)s' % {
            'page_number': page_number, 'message': str(err)})
    return items


def serialize_decimal(obj):
    if isinstance(obj, decimal.Decimal):
        return str(obj)
    return JSONEncoder.default(obj)


def create_superuser(credentials):
    user, created = User.objects.get_or_create(
        email=credentials['email'], defaults={
            'is_active': True, 'is_staff': True, 'is_superuser': True})
    if created:
        user.set_password(credentials['password'])
        user.save()
        msg = 'Superuser - %(email)s/%(password)s' % credentials
    else:
        msg = 'Superuser already exists - %(email)s' % credentials
    return msg
