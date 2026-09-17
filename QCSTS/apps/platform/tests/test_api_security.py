from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import CustomUser
from apps.platform.models import Membership, Organization, Permission, Role, Site


class PlatformApiSecurityTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            email="platform-api@example.test",
            password="TestPass123!",
            full_name="Platform API User",
        )
        self.other_user = CustomUser.objects.create_user(
            email="other-platform-api@example.test",
            password="TestPass123!",
            full_name="Other Platform API User",
        )
        self.organization = Organization.objects.create(
            name="Acme Pharma", slug="acme-pharma", country="EG"
        )
        self.other_organization = Organization.objects.create(
            name="Other Pharma", slug="other-pharma", country="EG"
        )
        self.site = Site.objects.create(
            organization=self.organization, name="Cairo QC", country="EG"
        )
        self.other_site = Site.objects.create(
            organization=self.other_organization, name="Alex QC", country="EG"
        )
        self.role = Role.objects.create(organization=self.organization, name="QC Manager")
        self.other_role = Role.objects.create(
            organization=self.other_organization, name="QC Manager"
        )
        self.membership = Membership.objects.create(
            user=self.user,
            organization=self.organization,
            role=self.role,
            default_site=self.site,
        )
        self.membership.sites.add(self.site)
        other_membership = Membership.objects.create(
            user=self.other_user,
            organization=self.other_organization,
            role=self.other_role,
            default_site=self.other_site,
        )
        other_membership.sites.add(self.other_site)
        self.client.force_authenticate(self.user)

    def grant(self, *codes):
        permissions = [
            Permission.objects.create(code=code, name=code) for code in codes
        ]
        self.role.permissions.add(*permissions)

    def test_site_list_is_tenant_scoped(self):
        self.grant("site.view")
        response = self.client.get(
            "/api/v1/platform/sites/",
            HTTP_X_ORGANIZATION_ID=str(self.organization.id),
        )

        self.assertEqual(response.status_code, 200)
        returned_ids = {item["id"] for item in response.data}
        self.assertEqual(returned_ids, {str(self.site.id)})
        self.assertNotIn(str(self.other_site.id), returned_ids)

    def test_foreign_site_detail_is_not_reachable(self):
        self.grant("site.view")
        response = self.client.get(
            f"/api/v1/platform/sites/{self.other_site.id}/",
            HTTP_X_ORGANIZATION_ID=str(self.organization.id),
        )

        self.assertEqual(response.status_code, 404)

    def test_site_create_requires_explicit_permission(self):
        response = self.client.post(
            "/api/v1/platform/sites/",
            {"name": "Unauthorized", "country": "EG"},
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.organization.id),
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(Site.objects.filter(name="Unauthorized").exists())

    def test_site_create_cannot_cross_tenant_boundary(self):
        self.grant("site.create")
        response = self.client.post(
            "/api/v1/platform/sites/",
            {
                "organization": str(self.other_organization.id),
                "name": "Spoofed Tenant",
                "country": "EG",
            },
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.organization.id),
        )

        self.assertEqual(response.status_code, 201)
        created = Site.objects.get(name="Spoofed Tenant")
        self.assertEqual(created.organization_id, self.organization.id)

    def test_site_update_requires_explicit_permission(self):
        response = self.client.patch(
            f"/api/v1/platform/sites/{self.site.id}/",
            {"name": "Unauthorized Rename"},
            format="json",
            HTTP_X_ORGANIZATION_ID=str(self.organization.id),
        )

        self.assertEqual(response.status_code, 403)
        self.site.refresh_from_db()
        self.assertEqual(self.site.name, "Cairo QC")

    def test_inactive_membership_cannot_use_platform_api(self):
        self.membership.is_active = False
        self.membership.save(update_fields=["is_active"])

        response = self.client.get(
            "/api/v1/platform/organizations/",
            HTTP_X_ORGANIZATION_ID=str(self.organization.id),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])
