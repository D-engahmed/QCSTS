from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.test import APIRequestFactory, force_authenticate
from django.test import TestCase

from apps.accounts.models import CustomUser
from apps.platform.models import Membership, Organization, Role, Site
from apps.platform.services import TenantContextService


def create_membership(user, slug, site_name):
    organization = Organization.objects.create(name=slug.title(), slug=slug, country="EG")
    site = Site.objects.create(organization=organization, name=site_name, country="EG")
    role = Role.objects.create(organization=organization, name=f"{slug}-analyst")
    membership = Membership.objects.create(
        user=user, organization=organization, role=role, default_site=site
    )
    membership.sites.add(site)
    return membership, site


class TestTenantContextService(TestCase):
    def create_user(self):
        return CustomUser.objects.create_user(
            email=f"user-{CustomUser.objects.count()}@example.test",
            password="TestPass123!",
            full_name="Test User",
        )

    def test_resolves_the_only_server_verified_membership(self):
        user = self.create_user()
        membership, site = create_membership(user, "acme", "Cairo")
        request = APIRequestFactory().get("/api/v1/products/")
        force_authenticate(request, user=user)
        request.user = user

        context = TenantContextService.resolve(request)

        assert context.organization_id == str(membership.organization_id)
        assert context.site_id == str(site.id)
        assert request.organization == membership.organization

    def test_rejects_an_organization_header_without_membership(self):
        user = self.create_user()
        create_membership(user, "acme", "Cairo")
        other = Organization.objects.create(name="Other", slug="other", country="EG")
        request = APIRequestFactory().get("/", HTTP_X_ORGANIZATION_ID=str(other.id))
        force_authenticate(request, user=user)
        request.user = user

        with self.assertRaises(PermissionDenied):
            TenantContextService.resolve(request)

    def test_requires_context_selection_when_user_has_multiple_memberships(self):
        user = self.create_user()
        create_membership(user, "acme", "Cairo")
        create_membership(user, "other", "Alexandria")
        request = APIRequestFactory().get("/")
        force_authenticate(request, user=user)
        request.user = user

        with self.assertRaises(ValidationError):
            TenantContextService.resolve(request)
