"""
Tenant-scoped view base classes.

Tenant-owned endpoints resolve their organization context before permission
checks. Concrete tenant views must explicitly declare an authorization policy;
falling back to the global DRF permission default is a production security bug.
"""

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from apps.platform.services import TenantContextService


class TenantExemptAPIView(APIView):
    """Explicitly opts out of tenant scoping for legitimate non-tenant APIs."""

    tenant_scoped = False


class PublicAPIView(TenantExemptAPIView):
    """Unauthenticated entry points such as login."""


class TenantScopedAPIView(APIView):
    """
    Base class for every endpoint that touches organization-owned data.

    Tenant context is resolved before DRF permission checks. Concrete views
    must define permission_classes themselves. This prevents a new endpoint
    from silently inheriting only global authentication and accidentally
    shipping without action-level RBAC.
    """

    tenant_scoped = True

    def perform_authentication(self, request):
        super().perform_authentication(request)
        if request.user and request.user.is_authenticated:
            TenantContextService.resolve(request)

    def get_permissions(self):
        """Fail closed when a tenant endpoint has no explicit authorization."""
        declared = self.__class__.__dict__.get("permission_classes")
        if declared is None:
            raise RuntimeError(
                f"{self.__class__.__name__} must explicitly declare permission_classes. "
                "TenantScopedAPIView must never rely on the global DRF default."
            )

        if any(permission is AllowAny for permission in declared):
            raise RuntimeError(
                f"{self.__class__.__name__} cannot use AllowAny on a tenant-scoped endpoint."
            )

        if len(declared) == 1 and declared[0] is IsAuthenticated:
            raise RuntimeError(
                f"{self.__class__.__name__} cannot use IsAuthenticated alone. "
                "Use a tenant-aware RBAC permission instead."
            )

        return super().get_permissions()

    def tenant_qs(self, queryset):
        """Restrict a queryset to the active organization."""
        return queryset.filter(organization=self.request.organization)

    def site_qs(self, queryset, field="site"):
        """Restrict a queryset to the active site after organization scoping."""
        queryset = self.tenant_qs(queryset)
        site = getattr(self.request, "site", None)
        if site is None:
            return queryset
        return queryset.filter(**{field: site})

    def tenant_create_kwargs(self, **extra):
        """Inject server-verified tenant ownership into create operations."""
        kwargs = {
            "organization": self.request.organization,
            "created_by": self.request.user,
        }
        kwargs.update(extra)
        return kwargs
