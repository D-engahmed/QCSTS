from decimal import Decimal

from django.test import TestCase

from apps.billing.models import EntitlementService, Plan, Subscription
from apps.platform.models import Organization


class BillingFoundationTests(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Example Pharma",
            slug="example-pharma",
            country="EG",
            timezone="Africa/Cairo",
            currency="USD",
        )
        self.plan = Plan.objects.create(
            code=Plan.Code.PROFESSIONAL,
            name="Professional",
            monthly_price=Decimal("899.00"),
            annual_price=Decimal("8990.00"),
            max_users=50,
            max_sites=3,
            max_studies=1000,
            max_storage_mb=102400,
            api_access=True,
        )

    def test_subscription_is_tenant_scoped(self):
        subscription = Subscription.objects.create(
            organization=self.organization,
            plan=self.plan,
            status=Subscription.Status.ACTIVE,
        )
        self.assertEqual(EntitlementService.subscription_for(self.organization), subscription)
        self.assertTrue(EntitlementService.can_use_api(self.organization))
        self.assertEqual(EntitlementService.limit_for(self.organization, "max_sites"), 3)

    def test_suspended_subscription_has_no_entitlements(self):
        Subscription.objects.create(
            organization=self.organization,
            plan=self.plan,
            status=Subscription.Status.SUSPENDED,
        )
        self.assertFalse(EntitlementService.has_active_subscription(self.organization))
        self.assertFalse(EntitlementService.can_use_api(self.organization))
        self.assertEqual(EntitlementService.limit_for(self.organization, "max_sites"), 0)
