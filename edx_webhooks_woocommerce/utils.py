from __future__ import unicode_literals

import logging

from django.db import transaction

from edx_webhooks.utils import enroll_in_course

from .models import WooCommerceOrder as Order
from .models import WooCommerceOrderItem as OrderItem


logger = logging.getLogger(__name__)


def record_order(data, action):
    return Order.objects.get_or_create(
        order_id=data.content['id'],
        action=action,
        defaults={
            'webhook': data,
            'email': data.content['billing']['email'],
            'first_name': data.content['billing']['first_name'],
            'last_name': data.content['billing']['last_name']
        }
    )


def process_order(order, data, send_email=False):
    if order.status == Order.PROCESSED:
        logger.warning('Order %s has already '
                       'been processed, ignoring' % order.order_id)
        return
    elif order.status == Order.ERROR:
        logger.warning('Order %s has previously '
                       'failed to process, ignoring' % order.order_id)
        return

    if order.status == Order.PROCESSING:
        logger.warning('Order %s is already '
                       'being processed, retrying' % order.order_id)
    else:
        # Start processing the order. A concurrent attempt to access the
        # same order will result in django_fsm.ConcurrentTransition on
        # save(), causing a rollback.
        order.start_processing()
        with transaction.atomic():
            order.save()

    # Process line items
    for item in data['line_items']:
        # Process the line item. If the enrollment throws
        # an exception, we throw that exception up the stack so we can
        # attempt to retry order processing.
        process_line_item(order, item)
        logger.debug('Successfully processed line item '
                     '%s for order %s' % (item, order.order_id))

    # Mark the order status
    order.finish_processing()
    with transaction.atomic():
        order.save()

    return order


def process_line_item(order, item):
    """Process a line item of an order.

    Extract sku and properties.email, create an OrderItem, create an
    enrollment, and mark the OrderItem as processed. Propagate any
    errors, to be handled up the stack.
    """

    # Fetch SKU from the item
    sku = item['sku']

    # Fetch the participant email address from the line item meta
    # data. meta_data is very quirky: it's a list of lists, with zero
    # or one nested list, which if it exists, contains exactly one
    # dictionary.
    email = None
    for meta in [m['value'] for m in item['meta_data']]:
        try:
            # If meta is itself not a list, this throws IndexError
            # which we catch.
            meta_item = meta[0]
            # If the item is not a dictionary, this throws TypeError
            # which we throw up the stack. If the item is expectedly a
            # dictionary but does not have a 'type' key, this throws
            # KeyError instead, which we catch.
            if meta_item['type'] == 'email':
                # OK, we've found a learner email address, let's use
                # that.
                email = meta_item['_value']
                break
        except (IndexError, KeyError):
            pass

    # Store line item, prop
    order_item, created = OrderItem.objects.get_or_create(
        order=order,
        sku=sku,
        email=email
    )

    if order_item.status == OrderItem.PROCESSED:
        logger.warning('Order item %s has already '
                       'been processed, ignoring' % order_item.order_id)
        return
    elif order_item.status == OrderItem.PROCESSING:
        logger.warning('Order item %s is already '
                       'being processed, retrying' % order_item.order_id)
    else:
        order_item.start_processing()
        with transaction.atomic():
            order_item.save()

    # Create an enrollment for the line item
    enroll_in_course(sku, email, action=order.action)

    # Mark the item as processed
    order_item.finish_processing()
    with transaction.atomic():
        order_item.save()

    return order_item
