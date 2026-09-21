from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from django.test import TestCase

from apps.accounts.models import CustomUser
from apps.billing.models import Plan, Subscription
from apps.platform.models import Membership, Organization, Site


class RegistrationFlowTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def payload(self, **overrides):
        data = {
            "organization_name": "Acme Pharma",
            "legal_name": "Acme Pharma LLC",
            "slug": "acme-pharma",
            "country": "EG",
            "timezone": "Africa/Cairo",
            "currency": "EGP",
            "site_name": "Cairo QC Laboratory",
            "site_address": "Cairo",
            "full_name": "Owner User",
            "email": "owner@acme.test",
            "password": "A-strong-password-123",
        }
        data.update(overrides)
        return data

    def test_registration_creates_tenant_site_owner_and_trial_subscription(self):
        response = self.client.post("/api/v1/auth/register/", self.payload(), format="json")

        self.assertEqual(response.status_code, 201)
        organization = Organization.objects.get(slug="acme-pharma")
        site = Site.objects.get(organization=organization)
        user = CustomUser.objects.get(email="owner@acme.test")
        membership = Membership.objects.get(user=user, organization=organization)
        subscription = Subscription.objects.get(organization=organization)

        self.assertEqual(site.name, "Cairo QC Laboratory")
        self.assertEqual(membership.default_site_id, site.id)
        self.assertTrue(membership.sites.filter(pk=site.id).exists())
        self.assertEqual(subscription.status, Subscription.Status.TRIALING)
        self.assertEqual(subscription.interval, Subscription.Interval.MONTH)
        self.assertGreater(subscription.trial_ends_at, timezone.now())

    def test_registration_without_site_name_still_has_default_site(self):
        response = self.client.post(
            "/api/v1/auth/register/",
            self.payload(site_name="", site_address=""),
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        organization = Organization.objects.get(slug="acme-pharma")
        site = Site.objects.get(organization=organization)
        self.assertEqual(site.name, "Primary Site")

    def test_new_staff_member_gets_default_site(self):
        self.client.post("/api/v1/auth/register/", self.payload(), format="json")
        owner = CustomUser.objects.get(email="owner@acme.test")
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(owner)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.post(
            "/api/v1/auth/users/",
            {
                "email": "analyst@acme.test",
                "full_name": "Analyst User",
                "role": "analyst",
                "password": "Another-strong-password-123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        staff = CustomUser.objects.get(email="analyst@acme.test")
        membership = Membership.objects.get(user=staff)
        self.assertIsNotNone(membership.default_site_id)
        self.assertTrue(membership.sites.filter(pk=membership.default_site_id).exists())
