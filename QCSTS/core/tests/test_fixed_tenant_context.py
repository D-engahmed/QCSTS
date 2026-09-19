import pytest
from rest_framework.exceptions import PermissionDenied

from apps.accounts.tests.factories import UserFactory
from apps.platform.models import Membership, Organization, Role, Site
from apps.platform.services import TenantContextService


class Request:
    def __init__(self, user, headers=None):
        self.user = user
        self.META = headers or {}


@pytest.mark.django_db
def test_context_is_derived_from_single_membership():
    user = UserFactory()
    request = Request(user)

    context = TenantContextService.resolve(request)

    assert context.organization_id == str(user.membership.organization_id)
    assert context.site_id == str(user.membership.site_id)
    assert request.organization == user.membership.organization
    assert request.site == user.membership.site
    assert request.role == user.membership.role


@pytest.mark.django_db
def test_mismatched_organization_header_cannot_switch_tenant():
    user = UserFactory()
    other_org = Organization.objects.create(
        name="Other Organization", slug="other-org", country="EG"
    )

    request = Request(
        user,
        {"HTTP_X_ORGANIZATION_ID": str(other_org.id)},
    )

    with pytest.raises(PermissionDenied):
        TenantContextService.resolve(request)


@pytest.mark.django_db
def test_mismatched_site_header_cannot_switch_site():
    user = UserFactory()
    other_site = Site.objects.create(
        organization=user.membership.organization,
        name="Other Site",
        country="EG",
    )

    request = Request(
        user,
        {"HTTP_X_SITE_ID": str(other_site.id)},
    )

    with pytest.raises(PermissionDenied):
        TenantContextService.resolve(request)


@pytest.mark.django_db
def test_organization_scope_keeps_fixed_site_identity_but_allows_org_scope():
    user = UserFactory()
    role = Role.objects.create(
        organization=user.membership.organization,
        name="admin",
        scope="ORGANIZATION",
    )
    user.membership.role = role
    user.membership.save(update_fields=["role"])

    request = Request(user)
    context = TenantContextService.resolve(request)

    assert context.site_id == str(user.membership.site_id)
    assert context.role_scope == "ORGANIZATION"
