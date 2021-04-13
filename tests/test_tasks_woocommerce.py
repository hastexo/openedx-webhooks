# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from requests.exceptions import HTTPError

from edx_webhooks.models import JSONWebhookData

from edx_webhooks_woocommerce.models import WooCommerceOrder as Order
from edx_webhooks_woocommerce.tasks import process
from edx_webhooks_woocommerce.utils import record_order

import requests_mock

from . import WooCommerceTestCase


class ProcessOrderTest(WooCommerceTestCase):

    def setUp(self):
        self.setup_payload()
        self.setup_webhook_data()
        self.setup_requests()

    def test_invalid_sku(self):
        fixup_payload = self.raw_payload.decode('utf-8').replace("course-v1:org+course+run1",  # noqa: E501
                                                                 "course-v1:org+nosuchcourse+run1")  # noqa: E501
        fixup_json_payload = json.loads(fixup_payload)
        fixup_webhook_data = JSONWebhookData(headers={},
                                             body=b'',
                                             content=fixup_json_payload)
        fixup_webhook_data.save()
        order, created = record_order(fixup_webhook_data, action=Order.ACTION_ENROLL)

        result = None
        with requests_mock.Mocker() as m:
            m.register_uri('POST',
                           self.token_uri,
                           json=self.token_response)
            m.register_uri('POST',
                           self.enroll_uri,
                           status_code=400)
            with self.assertRaises(HTTPError):
                result = process.delay(fixup_json_payload)
                result.get(5)

        self.assertEqual(result.state, 'FAILURE')

        # Even with the exception raised, it's the task failure
        # handler's job to set the status to ERROR. Given the async
        # nature of the task, though, the object reference doesn't
        # learn of the update until we read back the order. This can't
        # just use refresh_from_db(), because of the FSM-protected
        # status field.
        order = Order.objects.get(pk=order.id)
        self.assertEqual(order.status, Order.ERROR)

    def test_valid_order(self):
        order, created = record_order(self.webhook_data, action=Order.ACTION_ENROLL)

        result = None

        enrollment_response = {
            'action': 'enroll',
            'courses': {
                'course-v1:org+course+run1': {
                    'action': 'enroll',
                    'results': [
                        {
                            'identifier': 'learner@example.com',
                            'after': {
                                'enrollment': False,
                                'allowed': True,
                                'user': False,
                                'auto_enroll': True
                            },
                            'before': {
                                'enrollment': False,
                                'allowed': False,
                                'user': False,
                                'auto_enroll': False
                            }
                        }
                    ],
                    'auto_enroll': True}
            },
            'email_students': True,
            'auto_enroll': True
        }

        with requests_mock.Mocker() as m:
            m.register_uri('POST',
                           self.token_uri,
                           json=self.token_response)
            m.register_uri('POST',
                           self.enroll_uri,
                           json=enrollment_response)
            result = process.delay(self.json_payload)
            result.get(5)

        self.assertEqual(result.state, 'SUCCESS')

        # Read back the order (can't just use refresh_from_db(),
        # because of the FSM-protected status field)
        order = Order.objects.get(pk=order.id)
        self.assertEqual(order.status, Order.PROCESSED)

    def test_order_collision(self):
        order, created = record_order(self.webhook_data, action=Order.ACTION_ENROLL)

        enrollment_response = {
            'action': 'enroll',
            'courses': {
                'course-v1:org+course+run1': {
                    'action': 'enroll',
                    'results': [
                        {
                            'identifier': 'learner@example.com',
                            'after': {
                                'enrollment': False,
                                'allowed': True,
                                'user': False,
                                'auto_enroll': True
                            },
                            'before': {
                                'enrollment': False,
                                'allowed': False,
                                'user': False,
                                'auto_enroll': False
                            }
                        }
                    ],
                    'auto_enroll': True}
            },
            'email_students': True,
            'auto_enroll': True
        }

        with requests_mock.Mocker() as m:
            m.register_uri('POST',
                           self.token_uri,
                           json=self.token_response)
            m.register_uri('POST',
                           self.enroll_uri,
                           json=enrollment_response)
            result1 = process.delay(self.json_payload)
            result2 = process.delay(self.json_payload)
            result3 = process.delay(self.json_payload)
            result1.get(5)
            result2.get(5)
            result3.get(5)

        self.assertEqual(result1.state, 'SUCCESS')
        self.assertEqual(result2.state, 'SUCCESS')
        self.assertEqual(result3.state, 'SUCCESS')

        # Read back the order (can't just use refresh_from_db(),
        # because of the FSM-protected status field)
        order = Order.objects.get(pk=order.id)
        self.assertEqual(order.status, Order.PROCESSED)
