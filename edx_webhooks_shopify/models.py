from django.db.models import UniqueConstraint, ForeignKey
from django.db.models import PROTECT, SET_NULL

from edx_webhooks.models import Order, OrderItem, JSONWebhookData

APP_LABEL = 'edx_webhooks_shopify'


class ShopifyOrder(Order):

    class Meta:
        app_label = APP_LABEL
        abstract = False
        constraints = [
            UniqueConstraint(fields=['order_id', 'action'],
                             name='unique_order_id_action')
        ]

    webhook = ForeignKey(
        JSONWebhookData,
        on_delete=SET_NULL,
        null=True
    )


class ShopifyOrderItem(OrderItem):

    class Meta:
        app_label = APP_LABEL
        abstract = False
        constraints = [
            UniqueConstraint(fields=['order', 'sku', 'email'],
                             name='unique_order_sku_email')
        ]

    order = ForeignKey(
        ShopifyOrder,
        on_delete=PROTECT
    )
