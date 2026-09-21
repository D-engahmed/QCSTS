from decimal import Decimal
from unittest.mock import patch

from django.test import SimpleTestCase

from .paymob import calculate_transaction_hmac, verify_transaction_hmac


class PaymobHMACTests(SimpleTestCase):
    def setUp(self):
        self.obj = {
            "amount_cents": 39900,
            "created_at": "2026-09-21T00:00:00",
            "currency": "EGP",
            "error_occured": False,
            "has_parent_transaction": False,
            "id": 12345,
            "integration_id": 67890,
            "is_3d_secure": True,
            "is_auth": False,
            "is_capture": True,
            "is_refunded": False,
            "is_standalone_payment": True,
            "is_voided": False,
            "order": {"id": 98765},
            "owner": 123,
            "pending": False,
            "source_data": {"pan": "2346", "sub_type": "MasterCard", "type": "card"},
            "success": True,
        }

    def test_hmac_round_trip(self):
        signature = calculate_transaction_hmac(self.obj, "test-secret")
        self.assertTrue(verify_transaction_hmac(self.obj, signature, "test-secret"))

    def test_tampering_is_rejected(self):
        signature = calculate_transaction_hmac(self.obj, "test-secret")
        tampered = {**self.obj, "amount_cents": 1}
        self.assertFalse(verify_transaction_hmac(tampered, signature, "test-secret"))

    def test_missing_secret_is_rejected(self):
        self.assertFalse(verify_transaction_hmac(self.obj, None, ""))


class BillingAmountTests(SimpleTestCase):
    def test_invoice_amount_conversion_is_decimal_safe(self):
        total = Decimal("899.00")
        cents = int((total * Decimal("100")).quantize(Decimal("1")))
        self.assertEqual(cents, 89900)
