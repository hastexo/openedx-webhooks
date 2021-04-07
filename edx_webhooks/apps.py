"""
edX webhooks Django app configuration for Shopify integration.
"""

from django.apps import AppConfig


class EdXWebhooksConfig(AppConfig):
    """
    Configuration for the Shopify integration as an edX Django Plugin App.

    Django Plugin App configuration to be able to use the module as a standalone edX Plugin App.
    """

    name = "edx_webhooks"
    plugin_app = {
        "url_config": {
            "lms.djangoapp": {
                "namespace": "edx_webhooks",
            },
        },
        "settings_config": {
            "lms.djangoapp": {
                "common": {
                    "relative_path": "plugin"
                },
                "devstack": {
                    "relative_path": "plugin"
                },
                "production": {
                    "relative_path": "plugin"
                }
            }
        }
    }
