"""
edX webhooks Django app configuration for Shopify integration.
"""

from django.apps import AppConfig


class EdXWebhooksWoocommerceConfig(AppConfig):
    """
    Configuration for the Woocommerce integration as an edX Django Plugin App.

    Django Plugin App configuration to be able to use the module as a standalone edX Plugin App.
    """

    name = "edx_webhooks_woocommerce"
    plugin_app = {}
