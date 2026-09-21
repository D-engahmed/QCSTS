"""Tenant-scoped API and viewset base classes with release-critical controls."""

from rest_framework.permissions import AllowAny, IsAuthenticated, SAFE_METHODS
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from apps.billing.models import EntitlementService
from apps.platform.services import TenantContextService


class TenantExemptAPIView(APIView):
    tenant_scoped = False


class PublicAPIView(TenantExemptAPIView):
    pass


class TenantScopedAPIView(APIView):
    tenant_scoped = True
    billing_required = True

    def perform_authentication(self, request):
        super().perform_authentication(request)
        if request.user and request.user.is_authenticated:
            TenantContextService.resolve(request)

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        if self.billing_required and request.method not in SAFE_METHODS:
            EntitlementService.require_usable_subscription(request.organization)

    def get_permissions(self):
        declared = self.__class__.__dict__.get("permission_classes")
        if declared is None:
            raise RuntimeError(f"{self.__class__.__name__} must explicitly declare permission_classes.")
        if any(permission is AllowAny for permission in declared):
            raise RuntimeError(f"{self.__class__.__name__} cannot use AllowAny on a tenant-scoped endpoint.")
        if len(declared) == 1 and declared[0] is IsAuthenticated:
            raise RuntimeError(f"{self.__class__.__name__} cannot use IsAuthenticated alone. Use tenant-aware RBAC.")
        return super().get_permissions()

    def tenant_qs(self, queryset):
        return queryset.filter(organization=self.request.organization)

    def site_qs(self, queryset, field="site"):
        queryset = self.tenant_qs(queryset)
        site = getattr(self.request, "site", None)
        return queryset if site is None else queryset.filter(**{field: site})

    def tenant_create_kwargs(self, **extra):
        kwargs = {"organization": self.request.organization, "created_by": self.request.user}
        kwargs.update(extra)
        return kwargs


class TenantExemptViewSet(ReadOnlyModelViewSet):
    tenant_scoped = False


class TenantScopedViewSet(ReadOnlyModelViewSet):
    tenant_scoped = True
    billing_required = True

    def get_permissions(self):
        declared = self.__class__.__dict__.get("permission_classes")
        if declared is None:
            raise RuntimeError(f"{self.__class__.__name__} must explicitly declare permission_classes.")
        if any(permission is AllowAny for permission in declared):
            raise RuntimeError(f"{self.__class__.__name__} cannot use AllowAny on a tenant-scoped endpoint.")
        if len(declared) == 1 and declared[0] is IsAuthenticated:
            raise RuntimeError(f"{self.__class__.__name__} cannot use IsAuthenticated alone. Use tenant-aware RBAC.")
        return super().get_permissions()

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        if self.billing_required and request.method not in SAFE_METHODS:
            EntitlementService.require_usable_subscription(request.organization)

    def get_queryset(self):
        return TenantContextService.scope_queryset(self.request, self.queryset)


class TenantScopedModelViewSet(ModelViewSet):
    tenant_scoped = True
    billing_required = True

    def get_permissions(self):
        declared = self.__class__.__dict__.get("permission_classes")
        if declared is None:
            raise RuntimeError(f"{self.__class__.__name__} must explicitly declare permission_classes.")
        if any(permission is AllowAny for permission in declared):
            raise RuntimeError(f"{self.__class__.__name__} cannot use AllowAny on a tenant-scoped endpoint.")
        if len(declared) == 1 and declared[0] is IsAuthenticated:
            raise RuntimeError(f"{self.__class__.__name__} cannot use IsAuthenticated alone. Use tenant-aware RBAC.")
        return super().get_permissions()

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        if self.billing_required and request.method not in SAFE_METHODS:
            EntitlementService.require_usable_subscription(request.organization)

    def get_queryset(self):
        return TenantContextService.scope_queryset(self.request, self.queryset)

    def perform_create(self, serializer):
        TenantContextService.resolve(self.request)
        serializer.save(organization=self.request.organization, created_by=self.request.user)
