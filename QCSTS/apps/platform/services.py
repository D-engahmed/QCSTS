from dataclasses import dataclass

from rest_framework.exceptions import NotFound, PermissionDenied

from apps.platform.models import Membership


@dataclass(frozen=True)
class TenantContext:
    organization_id: str
    membership_id: str
    site_id: str
    role_id: str
    role_scope: str


class TenantContextService:
    """Resolves one fixed customer authorization context from the authenticated user."""

    ORGANIZATION_HEADER = "HTTP_X_ORGANIZATION_ID"
    SITE_HEADER = "HTTP_X_SITE_ID"

    @classmethod
    def resolve(cls, request):
        membership = (
            Membership.objects.select_related("organization", "site", "role")
            .filter(
                user=request.user,
                is_active=True,
                organization__status="active",
                site__status="active",
            )
            .first()
        )
        if membership is None:
            raise PermissionDenied("No active customer authorization assignment is available.")

        requested_organization_id = request.META.get(cls.ORGANIZATION_HEADER)
        if requested_organization_id and str(membership.organization_id) != requested_organization_id:
            raise PermissionDenied("The requested organization does not match your assigned organization.")

        requested_site_id = request.META.get(cls.SITE_HEADER)
        if requested_site_id and str(membership.site_id) != requested_site_id:
            raise PermissionDenied("The requested site does not match your assigned site.")

        context = TenantContext(
            organization_id=str(membership.organization_id),
            membership_id=str(membership.id),
            site_id=str(membership.site_id),
            role_id=str(membership.role_id),
            role_scope=membership.role.scope,
        )
        request.organization = membership.organization
        request.membership = membership
        request.site = membership.site
        request.role = membership.role
        request.tenant_context = context
        return context

    @classmethod
    def scope_queryset(cls, request, queryset):
        cls.resolve(request)
        return queryset.filter(organization=request.organization)
