# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import os

from django.conf import settings

from django.test import TestCase

from edx_webhooks.models import JSONWebhookData

from unittest.mock import Mock


class WebhookTestCase(TestCase):
    """Abstract base class for webhook tests"""
    PAYLOAD_FILENAME = None
    COURSE_ID_STRING = 'course-v1:org+course+run1'

    def setUp(self):
        self.setup_payload()
        self.setup_requests()

    def setup_payload(self):
        # Grab an example payload and make it available to test
        # methods as a raw string and as a JSON dictionary.
        payload_file = os.path.join(os.path.dirname(__file__),
                                    self.PAYLOAD_FILENAME)
        self.raw_payload = open(payload_file, 'rb').read()
        self.json_payload = json.load(open(payload_file, 'r'))

    def setup_webhook_data(self):
        self.webhook_data = JSONWebhookData(headers={},
                                            body=b'',
                                            content=self.json_payload)
        self.webhook_data.save()

    def setup_course(self):
        # TODO: Set up a mock course
        course = Mock()
        course.order_id = self.COURSE_ID_STRING

    def setup_requests(self):
        self.token_uri = '%s/oauth2/access_token' % settings.SOCIAL_AUTH_EDX_OAUTH2_URL_ROOT  # noqa: E501
        self.enroll_uri = '%s/api/bulk_enroll/v1/bulk_enroll/' % settings.SOCIAL_AUTH_EDX_OAUTH2_URL_ROOT  # noqa: E501

        self.token_response = {
            'access_token': 'foobar',
            'expires_in': 3600
        }


class ShopifyTestCase(WebhookTestCase):
    PAYLOAD_FILENAME = 'shopify.json'


class WooCommerceTestCase(WebhookTestCase):
    PAYLOAD_FILENAME = 'woocommerce.json'
