from dataclasses import dataclass

from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from apps.platform.models import Membership, Site, Organization


@dataclass(frozen=True)
class TenantContext:
    organization_id: str
    membership_id: str
    site_id: str | None


class TenantContextService:
    """Resolves browser context only from an active, server-verified membership."""

    ORGANIZATION_HEADER = "HTTP_X_ORGANIZATION_ID"
    SITE_HEADER = "HTTP_X_SITE_ID"

    @classmethod
    def resolve(cls, request):
        memberships = Membership.objects.select_related("organization", "default_site", "role").filter(
            user=request.user,
            is_active=True,
            organization__status="active",
        )
        requested_organization_id = request.META.get(cls.ORGANIZATION_HEADER)
        if requested_organization_id:
            membership = memberships.filter(organization_id=requested_organization_id).first()
            if not membership:
                raise PermissionDenied("You are not an active member of this organization.")
        else:
            membership = memberships.first()
            if not membership:
                raise PermissionDenied("No active organization membership is available.")
            if memberships.count() > 1:
                raise ValidationError({"organization": "Select an organization context."})

        requested_site_id = request.META.get(cls.SITE_HEADER)
        site = cls._resolve_site(membership, requested_site_id)
        context = TenantContext(
            organization_id=str(membership.organization_id),
            membership_id=str(membership.id),
            site_id=str(site.id) if site else None,
        )
        request.organization = membership.organization
        request.membership = membership
        request.site = site
        request.tenant_context = context
        return context

    @classmethod
    def scope_queryset(cls, request, queryset):
        cls.resolve(request)
        if queryset.model is Organization:
            return queryset.filter(pk=request.organization.pk)
        return queryset.filter(organization=request.organization)

    @staticmethod
    def _resolve_site(membership, requested_site_id):
        if not requested_site_id:
            return membership.default_site
        site = Site.objects.filter(id=requested_site_id, organization=membership.organization).first()
        if not site:
            raise NotFound("Site not found in the active organization.")
        if membership.sites.exists() and not membership.sites.filter(id=site.id).exists():
            raise PermissionDenied("You do not have access to this site.")
        return site
