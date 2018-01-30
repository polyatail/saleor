from django.template import Library

from ...order import OrderStatus

register = Library()


ERRORS = {}
SUCCESSES = {OrderStatus.SHIPPED,}


LABEL_DANGER = 'danger'
LABEL_SUCCESS = 'success'
LABEL_DEFAULT = 'default'


@register.inclusion_tag('status_label.html')
def render_status(status, status_display=None):
    if status in ERRORS:
        label_cls = LABEL_DANGER
    elif status in SUCCESSES:
        label_cls = LABEL_SUCCESS
    else:
        label_cls = LABEL_DEFAULT
    return {'label_cls': label_cls, 'status': status_display or status}


