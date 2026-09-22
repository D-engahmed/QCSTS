"""
Cross-tenant write-path IDOR via reference fields.

core/tests/test_tenant_isolation.py proves the READ side is scoped: another
tenant's records don't show up in lists or direct lookups. This file proves
the WRITE side: that an org cannot attach a NEW record to ANOTHER org's
existing batch, test point, or monograph by submitting its ID.

Every case here was independently confirmed exploitable before
core/serializers.py existed — verified by temporarily reverting
core.serializers.TenantScopedModelSerializer usage and watching these tests
fail with a 200/201 instead of 400/403/404.
"""

import pytest
from rest_framework.test import APIClient

from apps.accounts.tests.factories import UserFactory
from apps.batches.tests.factories import BatchFactory
from apps.platform.models import Membership, Organization, Role
from apps.billing.models import Plan, Subscription
from django.utils import timezone
from datetime import timedelta
from apps.products.tests.factories import MonographWithTestsFactory, ProductFactory


def make_tenant(slug):
    org = Organization.objects.create(name=slug.title(), slug=slug, country="EG")
    user = UserFactory(email=f"analyst@{slug}.test", role="analyst")
    Membership.objects.filter(user=user).delete()
    role, _ = Role.objects.get_or_create(organization=org, name="analyst")
    Membership.objects.create(user=user, organization=org, role=role)
    plan, _ = Plan.objects.get_or_create(
        code=Plan.Code.ESSENTIAL,
        defaults={
            "name": "Essential",
            "description": "Test plan",
            "monthly_price": 399,
            "annual_price": 3990,
            "currency": "USD",
            "max_users": 1000,
            "max_sites": 100,
            "max_studies": 1000,
            "max_storage_mb": 100000,
            "api_access": True,
        },
    )
    now = timezone.now()
    Subscription.objects.get_or_create(
        organization=org,
        status=Subscription.Status.TRIALING,
        defaults={
            "plan": plan,
            "interval": Subscription.Interval.MONTH,
            "provider": "test",
            "trial_ends_at": now + timedelta(days=30),
            "current_period_start": now,
            "current_period_end": now + timedelta(days=30),
        },
    )
    return org, user


def client_for(user, organization):
    c = APIClient()
    c.force_authenticate(user=user)
    c.credentials(HTTP_X_ORGANIZATION_ID=str(organization.id))
    return c


@pytest.fixture
def two_tenants(db):
    org_a, user_a = make_tenant("alpha-labs")
    org_b, user_b = make_tenant("beta-labs")

    monograph_a = MonographWithTestsFactory(created_by=user_a, organization=org_a)
    product_a = ProductFactory(created_by=user_a, organization=org_a, monograph=monograph_a)
    batch_a = BatchFactory(created_by=user_a, organization=org_a, product=product_a)
    test_point_a = batch_a.test_points.first()

    return {
        "org_a": org_a, "user_a": user_a,
        "org_b": org_b, "user_b": user_b,
        "monograph_a": monograph_a, "product_a": product_a,
        "batch_a": batch_a, "test_point_a": test_point_a,
    }


@pytest.mark.django_db
class TestCrossTenantReferenceFieldsAreRejected:
    def test_cannot_relocate_another_tenants_batch(self, two_tenants):
        c = client_for(two_tenants["user_b"], two_tenants["org_b"])
        response = c.post(
            "/api/v1/chamber/move/",
            {
                "batch": str(two_tenants["batch_a"].id),
                "new_shelf": "S9", "new_rack": "R9", "new_position": "P9",
            },
            format="json",
        )
        assert response.status_code == 400, (
            f"Expected validation to reject a foreign batch ID; got "
            f"{response.status_code}. A 200 means org B just relocated org A's "
            "physical stability sample."
        )
        two_tenants["batch_a"].refresh_from_db()
        assert two_tenants["batch_a"].shelf != "S9"

    def test_cannot_pull_a_sample_against_another_tenants_batch(self, two_tenants):
        c = client_for(two_tenants["user_b"], two_tenants["org_b"])
        response = c.post(
            "/api/v1/chamber/pulls/",
            {
                "batch": str(two_tenants["batch_a"].id),
                "test_point": str(two_tenants["test_point_a"].id),
                "qty_pulled": 1,
            },
            format="json",
        )
        assert response.status_code == 400, (
            f"Expected rejection; got {response.status_code}. A success here "
            "consumes org A's physical sample quantity from an org B request."
        )

    def test_cannot_create_a_product_against_another_tenants_monograph(self, two_tenants):
        c = client_for(two_tenants["user_b"], two_tenants["org_b"])
        response = c.post(
            "/api/v1/products/",
            {
                "name": "Injected product",
                "strength": "10mg",
                "dosage_form": "tablet",
                "monograph": str(two_tenants["monograph_a"].id),
            },
            format="json",
        )
        assert response.status_code == 400, (
            f"Expected rejection; got {response.status_code}. A success here "
            "lets org B attach a product to org A's approved monograph."
        )

    def test_cannot_create_a_batch_against_another_tenants_product(self, two_tenants):
        c = client_for(two_tenants["user_b"], two_tenants["org_b"])
        response = c.post(
            "/api/v1/batches/",
            {
                "product": str(two_tenants["product_a"].id),
                "batch_number": "INJECTED-0001",
                "mfg_date": "2026-01-01",
                "expiry_date": "2029-01-01",
                "incubation_date": "2026-01-01",
                "study_type": "long_term",
                "shelf": "S1", "rack": "R1", "position": "P1",
                "qty_placed": 10,
            },
            format="json",
        )
        assert response.status_code == 400, (
            f"Expected rejection; got {response.status_code}. A success here "
            "creates a stability batch under org A's product from org B."
        )


@pytest.mark.django_db
@pytest.mark.django_db
def test_tenant_serializer_makes_actor_fields_server_owned(two_tenants):
    from apps.stability.api import StorageConditionSerializer

    serializer = StorageConditionSerializer(
        data={
            "code": "50C",
            "name": "50°C / 20% RH",
            "created_by": str(two_tenants["user_b"].id),
            "organization": str(two_tenants["org_a"].id),
        },
        context={"request": type("Request", (), {"organization": two_tenants["org_a"]})()},
    )
    assert serializer.fields["created_by"].read_only is True
    assert serializer.fields["organization"].read_only is True


class TestTenantScopedFieldFailsClosedNotOpen:
    def test_write_without_request_context_raises_rather_than_validating_unscoped(
        self, two_tenants
    ):
        """
        A developer who instantiates a TenantScopedModelSerializer for a write
        without passing context={'request': request} must get a loud failure,
        not a silently-unscoped queryset. This is the mistake that shipped
        SamplePullListCreateView.post without a request context in the first
        place.
        """
        from apps.products.serializers import ProductSerializer

        serializer = ProductSerializer(
            data={
                "name": "No context test",
                "strength": "5mg",
                "dosage_form": "tablet",
                "monograph": str(two_tenants["monograph_a"].id),
            }
        )
        with pytest.raises(RuntimeError, match="organization in serializer context"):
            serializer.is_valid(raise_exception=True)

    def test_read_serialization_still_works_without_request_context(self, two_tenants):
        """The fix must not break the common read path that never had context."""
        from apps.products.serializers import ProductSerializer

        data = ProductSerializer(two_tenants["product_a"]).data
        assert data["id"] == str(two_tenants["product_a"].id)
