import pytest
from django.test import RequestFactory
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.accounts.tests.factories import AdminFactory, UserFactory
from apps.platform.models import Membership, Organization, Role, Site
from apps.platform.services import TenantContextService
from core.permissions import HasOrganizationPermission, HasTenantContext, MinimumRole
from core.views import TenantScopedAPIView, TenantScopedModelViewSet


@pytest.mark.django_db
def test_tenant_context_resolution_headers_sites_and_multiple_memberships():
    user = AdminFactory()
    membership = user.memberships.select_related("organization", "role").get()
    org = membership.organization
    site = Site.objects.create(organization=org, name="Main", country="EG")
    membership.default_site = site
    membership.sites.add(site)
    membership.save(update_fields=["default_site"])

    request = RequestFactory().get("/", HTTP_X_ORGANIZATION_ID=str(org.id), HTTP_X_SITE_ID=str(site.id))
    request.user = user
    context = TenantContextService.resolve(request)
    assert context.organization_id == str(org.id)
    assert request.site == site

    other_org = Organization.objects.create(name="Other", slug="other-org", country="EG")
    other_role = Role.objects.create(organization=other_org, name="admin")
    Membership.objects.create(user=user, organization=other_org, role=other_role)
    request = RequestFactory().get("/")
    request.user = user
    with pytest.raises(ValidationError):
        TenantContextService.resolve(request)

    request = RequestFactory().get("/", HTTP_X_ORGANIZATION_ID="00000000-0000-0000-0000-000000000000")
    request.user = user
    with pytest.raises(PermissionDenied):
        TenantContextService.resolve(request)

    request = RequestFactory().get("/", HTTP_X_ORGANIZATION_ID=str(org.id), HTTP_X_SITE_ID="00000000-0000-0000-0000-000000000000")
    request.user = user
    with pytest.raises(Exception):
        TenantContextService.resolve(request)


def test_permission_classes_use_membership_context():
    request = RequestFactory().get("/")
    request.user = type("U", (), {"is_authenticated": True})()
    membership = type("M", (), {
        "role": type("R", (), {"name": "admin"})(),
        "has_permission": lambda self, code: code == "site.create",
    })()
    request.membership = membership
    assert HasTenantContext().has_permission(request, None) is True
    assert MinimumRole().has_permission(request, None) is True

    request.membership.role.name = "unknown"
    assert MinimumRole().has_permission(request, None) is False

    permission = HasOrganizationPermission()
    with pytest.raises(RuntimeError):
        permission.has_permission(request, None)
    permission.permission_code = "site.create"
    request.membership.role.name = "admin"
    assert permission.has_permission(request, None) is True


def test_tenant_base_helpers_and_guardrails():
    request = RequestFactory().get("/")
    request.organization = object()
    request.user = object()
    request.site = object()

    view = TenantScopedAPIView()
    view.request = request
    qs = type("QS", (), {"filter": lambda self, **kwargs: kwargs})()
    assert view.tenant_qs(qs)["organization"] is request.organization
    assert view.site_qs(qs)["site"] is request.site
    assert view.tenant_create_kwargs()["organization"] is request.organization

    class Missing(TenantScopedAPIView):
        pass

    with pytest.raises(RuntimeError):
        Missing().get_permissions()

    class PublicTenant(TenantScopedAPIView):
        permission_classes = [AllowAny]

    with pytest.raises(RuntimeError):
        PublicTenant().get_permissions()

    class AuthOnly(TenantScopedAPIView):
        permission_classes = [IsAuthenticated]

    with pytest.raises(RuntimeError):
        AuthOnly().get_permissions()


@pytest.mark.django_db
def test_tenant_scoped_model_viewset_queryset_and_create_helpers():
    user = UserFactory()
    org = user.memberships.select_related("organization").get().organization
    request = RequestFactory().get("/", HTTP_X_ORGANIZATION_ID=str(org.id))
    request.user = user
    view = TenantScopedModelViewSet()
    view.request = request
    view.queryset = Organization.objects.all()
    assert list(view.get_queryset()) == [org]
