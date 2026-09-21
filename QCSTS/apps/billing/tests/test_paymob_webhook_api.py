from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from apps.billing.models import Invoice, PaymentEvent, Plan, Subscription
from apps.billing.paymob import calculate_transaction_hmac
from apps.platform.models import Organization


class PaymobWebhookAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.org = Organization.objects.create(
            name="Paymob Test Pharma",
            slug="paymob-test-pharma",
            country="EG",
            currency="EGP",
        )
        self.plan = Plan.objects.create(
            code=Plan.Code.PROFESSIONAL,
            name="Professional",
            description="Test plan",
            monthly_price=Decimal("899.00"),
            annual_price=Decimal("8990.00"),
            currency="EGP",
            max_users=50,
            max_sites=5,
            max_studies=100,
            max_storage_mb=102400,
        )
        now = timezone.now()
        self.subscription = Subscription.objects.create(
            organization=self.org,
            plan=self.plan,
            status=Subscription.Status.TRIALING,
            interval=Subscription.Interval.MONTH,
            current_period_start=now,
            current_period_end=now + timedelta(days=30),
        )
        self.invoice = Invoice.objects.create(
            organization=self.org,
            subscription=self.subscription,
            number="INV-PM-001",
            provider_order_id="98765",
            currency="EGP",
            subtotal=Decimal("899.00"),
            total=Decimal("899.00"),
            due_at=now + timedelta(days=1),
        )

        self.obj = {
            "amount_cents": 89900,
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
        self.secret = "test-secret"

    def payload(self, obj=None, signature=None):
        obj = obj or self.obj
        signature = signature or calculate_transaction_hmac(obj, self.secret)
        return {"obj": obj, "hmac": signature}

    def test_invalid_hmac_is_rejected(self):
        response = self.client.post(
            "/api/v1/billing/webhooks/paymob/transaction/",
            {"obj": self.obj, "hmac": "invalid"},
            format="json",
        )
        self.assertEqual(response.status_code, 403)
        self.assertFalse(PaymentEvent.objects.exists())

    def test_unknown_order_is_rejected(self):
        obj = {**self.obj, "order": {"id": 404404}}
        signature = calculate_transaction_hmac(obj, self.secret)
        response = self.client.post(
            "/api/v1/billing/webhooks/paymob/transaction/",
            {"obj": obj, "hmac": signature},
            format="json",
        )
        self.assertEqual(response.status_code, 404)

    def test_amount_mismatch_is_rejected(self):
        obj = {**self.obj, "amount_cents": 1}
        signature = calculate_transaction_hmac(obj, self.secret)
        response = self.client.post(
            "/api/v1/billing/webhooks/paymob/transaction/",
            {"obj": obj, "hmac": signature},
            format="json",
        )
        self.assertEqual(response.status_code, 409)
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.status, Invoice.Status.DRAFT)

    def test_success_marks_invoice_paid_and_subscription_active(self):
        response = self.client.post(
            "/api/v1/billing/webhooks/paymob/transaction/",
            self.payload(),
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.invoice.refresh_from_db()
        self.subscription.refresh_from_db()
        self.assertEqual(self.invoice.status, Invoice.Status.PAID)
        self.assertEqual(self.invoice.provider_transaction_id, "12345")
        self.assertEqual(self.subscription.status, Subscription.Status.ACTIVE)
        self.assertEqual(PaymentEvent.objects.count(), 1)

    def test_duplicate_event_is_idempotent(self):
        payload = self.payload()
        first = self.client.post(
            "/api/v1/billing/webhooks/paymob/transaction/",
            payload,
            format="json",
        )
        second = self.client.post(
            "/api/v1/billing/webhooks/paymob/transaction/",
            payload,
            format="json",
        )
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(second.json()["status"], "already_processed")
        self.assertEqual(PaymentEvent.objects.count(), 1)
