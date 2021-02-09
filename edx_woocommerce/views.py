from __future__ import unicode_literals

import logging
import json

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from edx_webhooks.utils import hmac_is_valid

from .utils import record_order
from .models import Order
from .tasks import process


logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def order_create(request):
    # Load configuration
    conf = settings.WEBHOOK_SETTINGS['edx_woocommerce']

    # Process request
    try:
        source = request.META['HTTP_X_WC_WEBHOOK_SOURCE']
    except KeyError:
        logger.error('Request is missing X-WC-Webhook-Source header')
        return HttpResponse(status=400)

    if (conf['source'] != source):
        logger.error('Unknown source %s' % source)
        return HttpResponse(status=403)

    try:
        hmac = request.META['HTTP_X_WC_WEBHOOK_SIGNATURE']
    except KeyError:
        logger.error('Request is missing X-WC-Webhook-Signature header')
        return HttpResponse(status=400)

    body = request.body
    if (not hmac_is_valid(conf['secret'],
                          body,
                          hmac)):
        logger.error('Failed to verify HMAC signature')
        return HttpResponse(status=403)

    try:
        data = json.loads(body.decode('utf-8'))
    except ValueError:
        logger.error('Unable to parse request body as UTF-8 JSON')
        return HttpResponse(status=400)

    # Record order
    order, created = record_order(data)
    if created:
        logger.info('Created order %s' % order.id)
    else:
        logger.info('Retrieved order %s' % order.id)

    send_email = conf.get('send_email', True)

    # Process order
    if order.status == Order.NEW:
        logger.info('Scheduling order %s for processing' % order.id)
        process.delay(data, send_email)
    else:
        logger.info('Order %s already processed, '
                    'nothing to do' % order.id)

    return HttpResponse(status=200)