"""Tenant-scoped API base classes with one fixed customer authorization context."""

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from apps.platform.services import TenantContextService


class TenantExemptAPIView(APIView):
    tenant_scoped = False


class PublicAPIView(TenantExemptAPIView):
    pass


class TenantScopedAPIView(APIView):
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
        if self.request.membership.role.scope == "ORGANIZATION":
            return queryset
        return queryset.filter(**{field: self.request.site})

    def tenant_create_kwargs(self, **extra):
        kwargs = {
            "organization": self.request.organization,
            "created_by": self.request.user,
        }
        kwargs.update(extra)
        return kwargs


class TenantExemptViewSet(ReadOnlyModelViewSet):
    tenant_scoped = False


class TenantScopedViewSet(ReadOnlyModelViewSet):
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
        queryset = TenantContextService.scope_queryset(self.request, self.queryset)
        if self.request.membership.role.scope == "ORGANIZATION":
            return queryset
        return queryset.filter(site=self.request.site) if hasattr(self.queryset.model, "site") else queryset


class TenantScopedModelViewSet(ModelViewSet):
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
        queryset = TenantContextService.scope_queryset(self.request, self.queryset)
        if self.request.membership.role.scope == "ORGANIZATION":
            return queryset
        if hasattr(self.queryset.model, "site"):
            return queryset.filter(site=self.request.site)
        return queryset

    def perform_create(self, serializer):
        TenantContextService.resolve(self.request)
        kwargs = {
            "organization": self.request.organization,
            "created_by": self.request.user,
        }
        if hasattr(serializer.Meta.model, "site"):
            kwargs["site"] = self.request.site
        serializer.save(**kwargs)
