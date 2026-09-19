"""Tenant-scoped API and viewset base classes.

Every API surface must explicitly declare whether it is tenant-scoped or
tenant-exempt. Tenant-scoped viewsets resolve the active organization before
authorization and scope querysets to it.
"""

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from apps.platform.services import TenantContextService


class TenantExemptAPIView(APIView):
    """Explicitly opts out of tenant scoping for legitimate non-tenant APIs."""

    tenant_scoped = False


class PublicAPIView(TenantExemptAPIView):
    """Unauthenticated entry points such as login."""

    pass


class TenantScopedAPIView(APIView):
    """Base class for organization-owned API endpoints."""

    tenant_scoped = True

    def perform_authentication(self, request):
        super().perform_authentication(request)
        if request.user and request.user.is_authenticated:
            TenantContextService.resolve(request)

    def get_permissions(self):
        declared = self.__class__.__dict__.get("permission_classes")
        if declared is None:
            raise RuntimeError(
                f"{self.__class__.__name__} must explicitly declare permission_classes."
            )
        if any(permission is AllowAny for permission in declared):
            raise RuntimeError(
                f"{self.__class__.__name__} cannot use AllowAny on a tenant-scoped endpoint."
            )
        if len(declared) == 1 and declared[0] is IsAuthenticated:
            raise RuntimeError(
                f"{self.__class__.__name__} cannot use IsAuthenticated alone. "
                "Use tenant-aware RBAC."
            )
        return super().get_permissions()

    def tenant_qs(self, queryset):
        return queryset.filter(organization=self.request.organization)

    def site_qs(self, queryset, field="site"):
        queryset = self.tenant_qs(queryset)
        site = getattr(self.request, "site", None)
        return queryset if site is None else queryset.filter(**{field: site})

    def tenant_create_kwargs(self, **extra):
        kwargs = {
            "organization": self.request.organization,
            "created_by": self.request.user,
        }
        kwargs.update(extra)
        return kwargs


class TenantExemptViewSet(ReadOnlyModelViewSet):
    """Explicitly opts out of active-tenant scoping for a documented reason."""

    tenant_scoped = False


class TenantScopedViewSet(ReadOnlyModelViewSet):
    """Read-only tenant-scoped viewset with explicit authorization."""

    tenant_scoped = True

    def get_permissions(self):
        declared = self.__class__.__dict__.get("permission_classes")
        if declared is None:
            raise RuntimeError(
                f"{self.__class__.__name__} must explicitly declare permission_classes."
            )
        if any(permission is AllowAny for permission in declared):
            raise RuntimeError(
                f"{self.__class__.__name__} cannot use AllowAny on a tenant-scoped endpoint."
            )
        if len(declared) == 1 and declared[0] is IsAuthenticated:
            raise RuntimeError(
                f"{self.__class__.__name__} cannot use IsAuthenticated alone. "
                "Use tenant-aware RBAC."
            )
        return super().get_permissions()

    def get_queryset(self):
        return TenantContextService.scope_queryset(self.request, self.queryset)


class TenantScopedModelViewSet(ModelViewSet):
    """Full CRUD tenant-scoped viewset with explicit authorization."""

    tenant_scoped = True

    def get_permissions(self):
        declared = self.__class__.__dict__.get("permission_classes")
        if declared is None:
            raise RuntimeError(
                f"{self.__class__.__name__} must explicitly declare permission_classes."
            )
        if any(permission is AllowAny for permission in declared):
            raise RuntimeError(
                f"{self.__class__.__name__} cannot use AllowAny on a tenant-scoped endpoint."
            )
        if len(declared) == 1 and declared[0] is IsAuthenticated:
            raise RuntimeError(
                f"{self.__class__.__name__} cannot use IsAuthenticated alone. "
                "Use tenant-aware RBAC."
            )
        return super().get_permissions()

    def get_queryset(self):
        return TenantContextService.scope_queryset(self.request, self.queryset)

    def perform_create(self, serializer):
        TenantContextService.resolve(self.request)
        serializer.save(
            organization=self.request.organization,
            created_by=self.request.user,
        )
