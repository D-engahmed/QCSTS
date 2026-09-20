from rest_framework import serializers
from rest_framework.permissions import BasePermission

from apps.stability.models import Protocol, ProtocolVersion, Specification, SpecificationVersion, StabilitySample, StabilityStudy, StorageCondition, StudyBatch, StudyTimepoint
from core.permissions import IsAdmin, IsAnalystOrAbove, IsReviewerOrAbove, IsViewer
from core.serializers import TenantScopedModelSerializer
from core.views import TenantScopedModelViewSet


class StabilityPermissionByAction(BasePermission):
    def has_permission(self, request, view):
        if view.action in {"list", "retrieve"}:
            return IsViewer().has_permission(request, view)
        if view.action == "create":
            return IsAnalystOrAbove().has_permission(request, view)
        if view.action in {"update", "partial_update"}:
            return IsReviewerOrAbove().has_permission(request, view)
        if view.action == "destroy":
            return IsAdmin().has_permission(request, view)
        return False


class StabilityTenantViewSet(TenantScopedModelViewSet):
    permission_classes = [StabilityPermissionByAction]


class StorageConditionSerializer(TenantScopedModelSerializer):
    class Meta:
        model = StorageCondition
        fields = "__all__"
        read_only_fields = ["id", "organization", "created_at", "updated_at"]


class ProtocolSerializer(TenantScopedModelSerializer):
    class Meta:
        model = Protocol
        fields = "__all__"
        read_only_fields = ["id", "organization", "created_at", "updated_at"]


class ProtocolVersionSerializer(TenantScopedModelSerializer):
    class Meta:
        model = ProtocolVersion
        fields = "__all__"
        read_only_fields = ["id", "organization", "approved_by", "approved_at", "created_at", "updated_at"]


class SpecificationSerializer(TenantScopedModelSerializer):
    class Meta:
        model = Specification
        fields = "__all__"
        read_only_fields = ["id", "organization", "created_at", "updated_at"]


class SpecificationVersionSerializer(TenantScopedModelSerializer):
    class Meta:
        model = SpecificationVersion
        fields = "__all__"
        read_only_fields = ["id", "organization", "approved_by", "approved_at", "created_at", "updated_at"]


class StabilityStudySerializer(TenantScopedModelSerializer):
    class Meta:
        model = StabilityStudy
        fields = "__all__"
        read_only_fields = ["id", "organization", "created_at", "updated_at"]


class StudyBatchSerializer(TenantScopedModelSerializer):
    class Meta:
        model = StudyBatch
        fields = "__all__"
        read_only_fields = ["id", "organization", "created_at", "updated_at"]


class StudyTimepointSerializer(TenantScopedModelSerializer):
    class Meta:
        model = StudyTimepoint
        fields = "__all__"
        read_only_fields = ["id", "organization", "created_at", "updated_at"]


class StabilitySampleSerializer(TenantScopedModelSerializer):
    class Meta:
        model = StabilitySample
        fields = "__all__"
        read_only_fields = ["id", "organization", "created_at", "updated_at"]


class StorageConditionViewSet(StabilityTenantViewSet):
    queryset = StorageCondition.objects.all()
    serializer_class = StorageConditionSerializer


class ProtocolViewSet(StabilityTenantViewSet):
    queryset = Protocol.objects.all()
    serializer_class = ProtocolSerializer


class ProtocolVersionViewSet(StabilityTenantViewSet):
    queryset = ProtocolVersion.objects.all()
    serializer_class = ProtocolVersionSerializer


class SpecificationViewSet(StabilityTenantViewSet):
    queryset = Specification.objects.all()
    serializer_class = SpecificationSerializer


class SpecificationVersionViewSet(StabilityTenantViewSet):
    queryset = SpecificationVersion.objects.all()
    serializer_class = SpecificationVersionSerializer


class StabilityStudyViewSet(StabilityTenantViewSet):
    queryset = StabilityStudy.objects.all()
    serializer_class = StabilityStudySerializer


class StudyBatchViewSet(StabilityTenantViewSet):
    queryset = StudyBatch.objects.all()
    serializer_class = StudyBatchSerializer


class StudyTimepointViewSet(StabilityTenantViewSet):
    queryset = StudyTimepoint.objects.all()
    serializer_class = StudyTimepointSerializer


class StabilitySampleViewSet(StabilityTenantViewSet):
    queryset = StabilitySample.objects.all()
    serializer_class = StabilitySampleSerializer
