from rest_framework import serializers, viewsets
from apps.platform.models import Organization, Site
from apps.platform.permissions import CanCreateSites, CanDeleteSites, CanUpdateSites, CanViewSites
from apps.platform.services import TenantContextService
from core.views import TenantExemptViewSet, TenantScopedModelViewSet


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ("id", "name", "legal_name", "slug", "country", "timezone", "currency", "status", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = ("id", "organization", "name", "address", "country", "timezone", "status", "created_at", "updated_at")
        read_only_fields = ("id", "organization", "created_at", "updated_at")


class OrganizationViewSet(TenantExemptViewSet):
    """Organization discovery is membership-scoped and intentionally does not require a selected tenant."""

    queryset = Organization.objects.none()

    permission_classes = []

    def get_permissions(self):
        from rest_framework.permissions import IsAuthenticated
        return [IsAuthenticated()]
    serializer_class = OrganizationSerializer

    def get_queryset(self):
        return Organization.objects.filter(
            memberships__user=self.request.user,
            memberships__is_active=True,
        ).distinct()


class SiteViewSet(TenantScopedModelViewSet):
    permission_classes = [CanViewSites]
    serializer_class = SiteSerializer
    queryset = Site.objects.all()

    def get_permissions(self):
        permission_map = {
            "list": CanViewSites,
            "retrieve": CanViewSites,
            "create": CanCreateSites,
            "update": CanUpdateSites,
            "partial_update": CanUpdateSites,
            "destroy": CanDeleteSites,
        }
        permission_class = permission_map.get(self.action, CanViewSites)
        return [permission_class()]

    def perform_create(self, serializer):
        TenantContextService.resolve(self.request)
        serializer.save(organization=self.request.organization)
