"""Cross-tenant and privilege-escalation regression tests.

These tests are intentionally adversarial: a valid user from organization A
must never gain access to organization B by changing IDs, organization headers,
site IDs, or submitted ownership fields.
"""

import pytest
from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import CustomUser
from apps.platform.models import Membership, Organization, Permission, Role, Site


class TenantSecurityMatrixTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.alice = CustomUser.objects.create_user(
            email="alice-security@example.test",
            password="TestPass123!",
            full_name="Alice Security",
        )
        self.bob = CustomUser.objects.create_user(
            email="bob-security@example.test",
            password="TestPass123!",
            full_name="Bob Security",
        )
        self.org_a = Organization.objects.create(
            name="Security Pharma A", slug="security-pharma-a", country="EG"
        )
        self.org_b = Organization.objects.create(
            name="Security Pharma B", slug="security-pharma-b", country="EG"
        )
        self.site_a = Site.objects.create(
            organization=self.org_a, name="A QC", country="EG"
        )
        self.site_b = Site.objects.create(
            organization=self.org_b, name="B QC", country="EG"
        )
        self.role_a = Role.objects.create(
            organization=self.org_a, name="A Operator"
        )
        self.role_b = Role.objects.create(
            organization=self.org_b, name="B Operator"
        )
        self.member_a = Membership.objects.create(
            user=self.alice,
            organization=self.org_a,
            role=self.role_a,
            default_site=self.site_a,
        )
        self.member_a.sites.add(self.site_a)
        self.member_b = Membership.objects.create(
            user=self.bob,
            organization=self.org_b,
            role=self.role_b,
            default_site=self.site_b,
        )
        self.member_b.sites.add(self.site_b)
        self.client.force_authenticate(self.alice)

    def grant_a(self, *codes):
        permissions = [
            Permission.objects.create(code=code, name=code) for code in codes
        ]
        self.role_a.permissions.add(*permissions)

    def headers(self, organization):
        return {"HTTP_X_ORGANIZATION_ID": str(organization.id)}

    def test_cross_tenant_site_read_returns_not_found(self):
        self.grant_a("site.view")
        response = self.client.get(
            f"/api/v1/platform/sites/{self.site_b.id}/",
            **self.headers(self.org_a),
        )
        assert response.status_code == 404

    def test_cross_tenant_site_cannot_be_updated(self):
        self.grant_a("site.update")
        response = self.client.patch(
            f"/api/v1/platform/sites/{self.site_b.id}/",
            {"name": "Compromised"},
            format="json",
            **self.headers(self.org_a),
        )
        assert response.status_code == 404
        self.site_b.refresh_from_db()
        assert self.site_b.name == "B QC"

    def test_cross_tenant_site_cannot_be_deleted(self):
        self.grant_a("site.delete")
        response = self.client.delete(
            f"/api/v1/platform/sites/{self.site_b.id}/",
            **self.headers(self.org_a),
        )
        assert response.status_code == 404
        assert Site.objects.filter(pk=self.site_b.pk).exists()

    def test_switching_organization_header_does_not_grant_membership(self):
        self.grant_a("site.view")
        response = self.client.get(
            "/api/v1/platform/sites/",
            **self.headers(self.org_b),
        )
        assert response.status_code in (403, 404)

    def test_site_create_ignores_submitted_foreign_organization(self):
        self.grant_a("site.create")
        response = self.client.post(
            "/api/v1/platform/sites/",
            {
                "organization": str(self.org_b.id),
                "name": "Attempted Cross Tenant Site",
                "country": "EG",
            },
            format="json",
            **self.headers(self.org_a),
        )
        assert response.status_code == 201
        created = Site.objects.get(name="Attempted Cross Tenant Site")
        assert created.organization_id == self.org_a.id

    def test_user_without_permission_cannot_update_own_tenant(self):
        response = self.client.patch(
            f"/api/v1/platform/sites/{self.site_a.id}/",
            {"name": "Unauthorized"},
            format="json",
            **self.headers(self.org_a),
        )
        assert response.status_code == 403
        self.site_a.refresh_from_db()
        assert self.site_a.name == "A QC"

    def test_user_without_permission_cannot_delete_own_tenant(self):
        response = self.client.delete(
            f"/api/v1/platform/sites/{self.site_a.id}/",
            **self.headers(self.org_a),
        )
        assert response.status_code == 403
        assert Site.objects.filter(pk=self.site_a.pk).exists()

    def test_membership_cannot_use_a_role_from_another_organization(self):
        with pytest.raises(Exception):
            Membership.objects.create(
                user=self.alice,
                organization=self.org_a,
                role=self.role_b,
            ).clean()

    def test_membership_default_site_must_belong_to_same_organization(self):
        membership = Membership(
            user=self.alice,
            organization=self.org_a,
            role=self.role_a,
            default_site=self.site_b,
        )
        with pytest.raises(Exception):
            membership.clean()
