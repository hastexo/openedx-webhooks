"""
edX webhooks Django app settings for Shopify integration.
"""

import os


def get_setting(settings, setting_key, default_val=None):
    """
    Retrieves the value of the requested setting

    Gets the Value of an Environment variable either from
    the OS Environment or from the settings ENV_TOKENS

    Arguments:
        - settings (dict): Django settings
        - setting_key (str): String
        - default_val (str): String

    Returns:
        - Value of the requested setting (String)
    """

    setting_val = os.environ.get(setting_key, default_val)

    if hasattr(settings, "ENV_TOKENS"):
        return settings.ENV_TOKENS.get(setting_key, setting_val)

    return setting_val


def plugin_settings(settings):
    """
    Specifies django environment settings

    Extend django settings with the plugin defined ones to be able to configure
    the plugin individually.

    Arguments:
        settings (dict): Django settings

    Returns:
        None
    """

    settings.WEBHOOK_SETTINGS = {
        "edx_webhooks_shopify": {
            "shop_domain": get_setting(settings, "EDX_WEBHOOKS_SHOPIFY_SHOP_DOMAIN", default_val=""),
            "api_key": get_setting(settings, "EDX_WEBHOOKS_SHOPIFY_API_KEY", default_val=""),
        },
        "edx_webhooks_woocommerce": {
            "source": get_setting(settings, "EDX_WEBHOOKS_WOOCOMMERCE_SOURCE", default_val=""),
            "secret": get_setting(settings, "EDX_WEBHOOKS_WOOCOMMERCE_SECRET", default_val=""),
        },
    }
