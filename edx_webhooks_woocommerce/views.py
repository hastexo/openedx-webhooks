from __future__ import unicode_literals

import logging

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from edx_webhooks.utils import receive_json_webhook, hmac_is_valid
from edx_webhooks.utils import fail_and_save, finish_and_save
from .utils import record_order
from .models import WooCommerceOrder as Order
from .tasks import process


logger = logging.getLogger(__name__)


def extract_webhook_data(func):
    """
    Validate the incoming webhook and extract its content.

    Ensure that the necessary parameters are set on the incoming request. In case the
    data is valid, extract it and pass directly to the wrapped function
    """
    def inner(request):
        # Load configuration
        conf = settings.WEBHOOK_SETTINGS['edx_webhooks_woocommerce']

        try:
            data = receive_json_webhook(request)
        except Exception:
            return HttpResponse(status=400)

        source = data.headers.get('X-Wc-Webhook-Source')
        if not source:
            logger.error('Request is missing X-Wc-Webhook-Source header')
            fail_and_save(data)
            return HttpResponse(status=400)

        if conf['source'] != source:
            logger.error('Unknown source %s' % source)
            fail_and_save(data)
            return HttpResponse(status=403)

        hmac = data.headers.get('X-Wc-Webhook-Signature')
        if not hmac:
            logger.error('Request is missing X-Wc-Webhook-Signature header')
            fail_and_save(data)
            return HttpResponse(status=400)

        if not hmac_is_valid(conf['secret'], data.body, hmac):
            logger.error('Failed to verify HMAC signature')
            fail_and_save(data)
            return HttpResponse(status=403)

        finish_and_save(data)

        return func(request, conf, data)

    return inner


@csrf_exempt
@require_POST
@extract_webhook_data
def order_create(_, conf, data):
    # Record order
    order, created = record_order(data, action=Order.ACTION_ENROLL)
    if created:
        logger.info('Created order %s' % order.order_id)
    else:
        logger.info('Retrieved order %s' % order.order_id)

    send_email = conf.get('send_email', True)

    # Process order
    if order.status == Order.NEW:
        logger.info('Scheduling order %s for processing' % order.order_id)
        process.delay(data.content, send_email)
    else:
        logger.info('Order %s already processed, '
                    'nothing to do' % order.order_id)

    return HttpResponse(status=200)


@csrf_exempt
@require_POST
@extract_webhook_data
def order_delete(_, conf, data):
    # Record order deletion
    order, created = record_order(data, action=Order.ACTION_UNENROLL)
    if created:
        logger.info('Created order %s' % order.order_id)
    else:
        logger.info('Retrieved order %s' % order.order_id)

    send_email = conf.get('send_email', True)

    # Process order
    if order.status == Order.NEW:
        logger.info('Scheduling order %s for processing' % order.order_id)
        process.delay(data.content, send_email)
    else:
        logger.info('Order %s already processed, nothing to do' % order.order_id)

    return HttpResponse(status=200)
