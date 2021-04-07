"""
edX webhooks Django app configuration for Shopify integration.
"""

from django.apps import AppConfig


class EdXWebhooksShopifyConfig(AppConfig):
    """
    Configuration for the Shopify integration as an edX Django Plugin App.

    Django Plugin App configuration to be able to use the module as a standalone edX Plugin App.
    """

    name = "edx_webhooks_shopify"
    plugin_app = {}
