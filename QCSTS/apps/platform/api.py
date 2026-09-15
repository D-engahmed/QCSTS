from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAuthenticated
from apps.platform.models import Organization, Site, Membership
from apps.platform.services import TenantContextService


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


class OrganizationViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrganizationSerializer
    def get_queryset(self):
        return Organization.objects.filter(memberships__user=self.request.user, memberships__is_active=True).distinct()


class SiteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = SiteSerializer
    def get_queryset(self):
        return TenantContextService.scope_queryset(self.request, Site.objects.all())
    def perform_create(self, serializer):
        TenantContextService.resolve(self.request)
        serializer.save(organization=self.request.organization)
