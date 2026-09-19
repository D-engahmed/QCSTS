from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

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
    """Returns only the authenticated customer's single organization."""

    permission_classes = [IsAuthenticated]
    serializer_class = OrganizationSerializer

    def list(self, request, *args, **kwargs):
        TenantContextService.resolve(request)
        return Response(self.get_serializer(request.organization).data)

    def retrieve(self, request, *args, **kwargs):
        TenantContextService.resolve(request)
        if str(kwargs.get("pk")) != str(request.organization.id):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You cannot access another organization.")
        return Response(self.get_serializer(request.organization).data)

    def get_queryset(self):
        return Organization.objects.filter(pk=self.request.user.membership.organization_id)


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
        return [permission_map.get(self.action, CanViewSites)()]

    def get_queryset(self):
        TenantContextService.resolve(self.request)
        return Site.objects.filter(organization=self.request.organization)

    def perform_create(self, serializer):
        TenantContextService.resolve(self.request)
        serializer.save(organization=self.request.organization)
