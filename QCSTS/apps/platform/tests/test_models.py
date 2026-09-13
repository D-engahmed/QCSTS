from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.accounts.models import CustomUser
from apps.platform.models import Membership, Organization, Permission, Role, Site


class TestPlatformModels(TestCase):
    def create_user(self):
        return CustomUser.objects.create_user(
            email=f"user-{CustomUser.objects.count()}@example.test",
            password="TestPass123!",
            full_name="Test User",
        )

    def test_membership_permission_is_centrally_resolved(self):
        organization = Organization.objects.create(name="Acme Pharma", slug="acme", country="EG")
        permission = Permission.objects.create(code="study.create", name="Create studies")
        role = Role.objects.create(organization=organization, name="Analyst")
        role.permissions.add(permission)
        membership = Membership.objects.create(
            user=self.create_user(), organization=organization, role=role
        )

        assert membership.has_permission("study.create") is True
        assert membership.has_permission("study.approve") is False

    def test_membership_rejects_role_from_another_organization(self):
        first = Organization.objects.create(name="Acme Pharma", slug="acme", country="EG")
        second = Organization.objects.create(name="Other Pharma", slug="other", country="SA")
        role = Role.objects.create(organization=first, name="QA Manager")
        membership = Membership(user=self.create_user(), organization=second, role=role)

        with self.assertRaises(ValidationError):
            membership.full_clean()

    def test_membership_rejects_default_site_from_another_organization(self):
        first = Organization.objects.create(name="Acme Pharma", slug="acme", country="EG")
        second = Organization.objects.create(name="Other Pharma", slug="other", country="SA")
        role = Role.objects.create(organization=first, name="Analyst")
        foreign_site = Site.objects.create(organization=second, name="Riyadh", country="SA")
        membership = Membership(
            user=self.create_user(), organization=first, role=role, default_site=foreign_site
        )

        with self.assertRaises(ValidationError):
            membership.full_clean()
