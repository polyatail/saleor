from celery import shared_task
from django.conf import settings
from templated_email import send_templated_mail

CONFIRM_ORDER_TEMPLATE = 'order/confirm_order'
CONFIRM_PAYMENT_TEMPLATE = 'order/payment/confirm_payment'


def _send_confirmation(address, url, template):
    send_templated_mail(
        from_email=settings.ORDER_FROM_EMAIL,
        recipient_list=[address],
        context={'site_name': settings.SITE_NAME,
                 'url': url},
        template_name=template)


@shared_task
def send_order_confirmation(address, url):
    _send_confirmation(address, url, CONFIRM_ORDER_TEMPLATE)


@shared_task
def send_payment_confirmation(address, url):
    _send_confirmation(address, url, CONFIRM_PAYMENT_TEMPLATE)
