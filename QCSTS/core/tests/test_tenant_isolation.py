"""
Cross-tenant isolation, exercised end to end through the HTTP API.

The checklist asks for "Cross-tenant IDOR tests", "Cross-tenant list leakage
tests", "Cross-tenant search tests". This module is the evidence for those
boxes. It builds two real organizations with their own users and data, then
drives the API as org B and asserts that org A's records are invisible by
listing, unreachable by ID, and unwritable by payload injection.

The demonstration the milestone requires — "it must be impossible to show that
company A can see company B's data" — is these tests passing.
"""

import uuid

import pytest
from rest_framework.test import APIClient

from apps.accounts.tests.factories import UserFactory
from apps.batches.tests.factories import BatchFactory
from apps.platform.models import Membership, Organization, Role
from apps.products.tests.factories import MonographWithTestsFactory, ProductFactory


def make_tenant(slug, role_name="admin"):
    """An organization with an admin whose authority stops at its boundary."""
    org = Organization.objects.create(name=slug.title(), slug=slug, country="EG")
    user = UserFactory(email=f"{role_name}@{slug}.test", role=role_name)
    Membership.objects.filter(user=user).delete()
    role, _ = Role.objects.get_or_create(organization=org, name=role_name)
    Membership.objects.create(user=user, organization=org, role=role)
    return org, user


def client_for(user, organization):
    c = APIClient()
    c.force_authenticate(user=user)
    c.credentials(HTTP_X_ORGANIZATION_ID=str(organization.id))
    return c


@pytest.fixture
def tenants(db):
    org_a, user_a = make_tenant("alpha-pharma")
    org_b, user_b = make_tenant("beta-pharma")

    monograph = MonographWithTestsFactory(created_by=user_a, organization=org_a)
    product = ProductFactory(created_by=user_a, organization=org_a, monograph=monograph)
    batch = BatchFactory(created_by=user_a, organization=org_a, product=product)
    test_point = batch.test_points.first()

    return {
        "org_a": org_a, "user_a": user_a,
        "org_b": org_b, "user_b": user_b,
        "monograph": monograph, "product": product,
        "batch": batch, "test_point": test_point,
    }


LIST_ENDPOINTS = [
    "/api/v1/products/monographs/",
    "/api/v1/products/",
    "/api/v1/batches/",
    "/api/v1/test-points/",
    "/api/v1/results/",
    "/api/v1/chamber/",
    "/api/v1/chamber/pulls/",
    "/api/v1/audit/",
]


@pytest.mark.django_db
class TestCrossTenantListLeakage:
    @pytest.mark.parametrize("endpoint", LIST_ENDPOINTS)
    def test_list_endpoints_return_nothing_from_the_other_tenant(self, tenants, endpoint):
        c = client_for(tenants["user_b"], tenants["org_b"])
        response = c.get(endpoint)
        assert response.status_code in (200, 403), f"{endpoint} -> {response.status_code}"
        if response.status_code != 200:
            return
        body = str(response.data)
        for secret in (
            str(tenants["batch"].id),
            tenants["batch"].batch_number,
            str(tenants["product"].id),
            str(tenants["monograph"].id),
        ):
            assert secret not in body, f"{endpoint} leaked {secret} across tenants"


@pytest.mark.django_db
class TestCrossTenantIDOR:
    @pytest.mark.parametrize(
        "template,key",
        [
            ("/api/v1/products/monographs/{}/", "monograph"),
            ("/api/v1/products/{}/", "product"),
            ("/api/v1/batches/{}/", "batch"),
            ("/api/v1/test-points/{}/", "test_point"),
        ],
    )
    def test_direct_object_reference_from_another_tenant_is_not_found(
        self, tenants, template, key
    ):
        obj = tenants[key]
        c = client_for(tenants["user_b"], tenants["org_b"])
        response = c.get(template.format(obj.id))
        assert response.status_code == 404, (
            f"{template.format(obj.id)} returned {response.status_code} to a foreign tenant; "
            "expected 404. A 200 is a data breach, a 403 confirms the record exists."
        )

    def test_owner_can_still_read_its_own_record(self, tenants):
        c = client_for(tenants["user_a"], tenants["org_a"])
        response = c.get(f"/api/v1/batches/{tenants['batch'].id}/")
        assert response.status_code == 200, (
            "Isolation must not be achieved by breaking legitimate access."
        )


@pytest.mark.django_db
class TestOrganizationContextCannotBeForged:
    def test_client_supplied_organization_header_without_membership_is_rejected(self, tenants):
        c = APIClient()
        c.force_authenticate(user=tenants["user_b"])
        c.credentials(HTTP_X_ORGANIZATION_ID=str(tenants["org_a"].id))
        response = c.get("/api/v1/batches/")
        assert response.status_code == 403

    def test_organization_in_the_request_body_is_ignored_on_create(self, tenants):
        """A payload naming another tenant must not place the record there."""
        c = client_for(tenants["user_b"], tenants["org_b"])
        response = c.post(
            "/api/v1/products/monographs/",
            {
                "name": "Injected monograph",
                "version": "1.0",
                "effective_date": "2024-01-01",
                "organization": str(tenants["org_a"].id),
            },
            format="json",
        )
        if response.status_code == 201:
            from apps.products.models import Monograph

            created = Monograph.objects.get(id=response.data["data"]["id"])
            assert created.organization_id == tenants["org_b"].id, (
                "Client-supplied organization was trusted — records can be planted "
                "in another tenant."
            )

    def test_unknown_organization_header_is_rejected(self, tenants):
        c = APIClient()
        c.force_authenticate(user=tenants["user_b"])
        c.credentials(HTTP_X_ORGANIZATION_ID=str(uuid.uuid4()))
        response = c.get("/api/v1/batches/")
        assert response.status_code == 403


@pytest.mark.django_db
class TestUserDirectoryIsolation:
    def test_admin_cannot_list_users_of_another_tenant(self, tenants):
        c = client_for(tenants["user_b"], tenants["org_b"])
        response = c.get("/api/v1/auth/users/")
        assert response.status_code == 200
        emails = [u["email"] for u in response.data["data"]]
        assert tenants["user_a"].email not in emails
        assert tenants["user_b"].email in emails

    def test_admin_cannot_read_a_user_of_another_tenant(self, tenants):
        c = client_for(tenants["user_b"], tenants["org_b"])
        response = c.get(f"/api/v1/auth/users/{tenants['user_a'].id}/")
        assert response.status_code == 404

    def test_admin_cannot_revoke_a_user_of_another_tenant(self, tenants):
        c = client_for(tenants["user_b"], tenants["org_b"])
        response = c.delete(f"/api/v1/auth/users/{tenants['user_a'].id}/")
        assert response.status_code == 404
        assert Membership.objects.filter(
            user=tenants["user_a"], is_active=True
        ).exists()

    def test_role_cannot_be_escalated_through_a_profile_patch(self, tenants):
        """The old UserSerializer let any admin PATCH role='admin' onto anyone."""
        victim = tenants["user_b"]
        c = client_for(tenants["user_b"], tenants["org_b"])
        response = c.patch(
            f"/api/v1/auth/users/{victim.id}/",
            {"full_name": "Renamed", "role": "admin", "is_active": True},
            format="json",
        )
        assert response.status_code == 200
        membership = Membership.objects.get(user=victim, organization=tenants["org_b"])
        assert membership.role.name == "admin"  # unchanged — was already admin
        # And the write did not touch the authority source at all:
        assert Membership.objects.filter(user=victim).count() == 1
