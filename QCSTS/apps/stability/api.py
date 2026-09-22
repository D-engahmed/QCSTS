from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission
from rest_framework.response import Response

from apps.compliance.models import ElectronicSignature
from apps.platform.permissions import HasTenantContext
from apps.stability.models import (
    ControlledStatus,
    Protocol, ProtocolVersion, Specification, SpecificationVersion,
    StabilitySample, StabilityStudy, StorageCondition, StudyBatch, StudyTimepoint,
)
from core.permissions import IsAdmin, IsAnalystOrAbove, IsReviewerOrAbove, IsViewer
from core.responses import error_response
from core.serializers import TenantScopedModelSerializer
from core.views import TenantScopedModelViewSet
from services.audit_service import AuditService
from services.signature_service import SignatureService


class StabilityPermissionByAction(BasePermission):
    def has_permission(self, request, view):
        if getattr(view, "action", None) in {"list", "retrieve"}:
            return IsViewer().has_permission(request, view)
        if getattr(view, "action", None) == "create":
            return IsAnalystOrAbove().has_permission(request, view)
        if getattr(view, "action", None) in {"update", "partial_update"}:
            return IsReviewerOrAbove().has_permission(request, view)
        if getattr(view, "action", None) == "destroy":
            return IsAdmin().has_permission(request, view)
        if getattr(view, "action", None) in {"approve", "transition"}:
            return IsReviewerOrAbove().has_permission(request, view)
        return HasTenantContext().has_permission(request, view)


class StabilityTenantViewSet(TenantScopedModelViewSet):
    permission_classes = [StabilityPermissionByAction]

    def perform_destroy(self, instance):
        # Stability records are historical controlled records: never hard-delete.
        instance.soft_delete(
            deleted_by=self.request.user,
            ip_address=self.request.META.get("REMOTE_ADDR"),
            notes="Stability record retired through API.",
        )

    @action(detail=True, methods=["post"], url_path="transition")
    @transaction.atomic
    def transition(self, request, pk=None):
        obj = self.get_object()
        target = (request.data.get("status") or "").strip().lower()
        comments = (request.data.get("comments") or "").strip()
        allowed = self.allowed_transitions(obj)
        if target not in allowed.get(obj.status, set()):
            return error_response(
                f"Invalid transition from {obj.status} to {target}.",
                status_code=400,
            )
        if not comments:
            return error_response("Transition comments are required.", status_code=400)

        if target in {"approved", "effective", "completed", "closed", "superseded"}:
            token = request.headers.get("X-Signature-Token")
            if not token or not SignatureService.validate(request.user, token):
                return error_response("Valid electronic signature authentication is required.", status_code=403)

        old = obj.status
        obj.status = target
        obj.save(update_fields=["status", "updated_at"])
        if target in {"approved", "effective", "completed", "closed"}:
            ElectronicSignature.issue(
                organization=request.organization,
                signer=request.user,
                record_type=obj.__class__.__name__,
                record_id=obj.id,
                record_version=str(obj.updated_at.timestamp()),
                meaning=(
                    ElectronicSignature.Meaning.APPROVAL
                    if target in {"approved", "effective", "completed"}
                    else ElectronicSignature.Meaning.CLOSURE
                ),
                reason=comments,
                authentication_secret=settings.SECRET_KEY,
            )
        AuditService.log(
            performed_by=request.user,
            action="APPROVE" if target in {"approved", "effective"} else "UPDATE",
            model_name=obj.__class__.__name__,
            object_id=obj.id,
            object_repr=str(obj),
            old_value={"status": old},
            new_value={"status": target, "comments": comments},
            ip_address=request.META.get("REMOTE_ADDR"),
            organization=request.organization,
            notes="Controlled stability lifecycle transition.",
        )
        return Response(self.get_serializer(obj).data)

    def allowed_transitions(self, obj):
        if isinstance(obj, (ProtocolVersion, SpecificationVersion)):
            return {
                "draft": {"approved"},
                "approved": {"effective", "superseded"},
                "effective": {"superseded"},
                "superseded": set(),
                "inactive": set(),
            }
        if isinstance(obj, StabilityStudy):
            return {
                "draft": {"planned", "canceled"},
                "planned": {"active", "canceled"},
                "active": {"completed", "canceled"},
                "completed": {"closed"},
                "closed": set(),
                "canceled": set(),
            }
        if isinstance(obj, StudyTimepoint):
            return {
                "planned": {"open", "canceled"},
                "open": {"completed", "canceled"},
                "completed": set(),
                "canceled": set(),
            }
        if isinstance(obj, StabilitySample):
            return {
                "stored": {"pulled", "disposed", "retained"},
                "pulled": {"testing", "disposed"},
                "testing": {"completed", "disposed"},
                "completed": {"retained", "disposed"},
                "disposed": set(),
                "retained": set(),
            }
        return {}


class StorageConditionSerializer(TenantScopedModelSerializer):
    class Meta:
        model = StorageCondition
        fields = "__all__"
        read_only_fields = ["id", "organization", "created_at", "updated_at", "status"]


class ProtocolSerializer(TenantScopedModelSerializer):
    class Meta:
        model = Protocol
        fields = "__all__"
        read_only_fields = ["id", "organization", "created_at", "updated_at", "status"]


class ProtocolVersionSerializer(TenantScopedModelSerializer):
    class Meta:
        model = ProtocolVersion
        fields = "__all__"
        read_only_fields = ["id", "organization", "approved_by", "approved_at", "created_at", "updated_at", "status"]


class SpecificationSerializer(TenantScopedModelSerializer):
    class Meta:
        model = Specification
        fields = "__all__"
        read_only_fields = ["id", "organization", "created_at", "updated_at", "status"]


class SpecificationVersionSerializer(TenantScopedModelSerializer):
    class Meta:
        model = SpecificationVersion
        fields = "__all__"
        read_only_fields = ["id", "organization", "approved_by", "approved_at", "created_at", "updated_at", "status"]


class StabilityStudySerializer(TenantScopedModelSerializer):
    class Meta:
        model = StabilityStudy
        fields = "__all__"
        read_only_fields = ["id", "organization", "created_at", "updated_at", "status"]


class StudyBatchSerializer(TenantScopedModelSerializer):
    class Meta:
        model = StudyBatch
        fields = "__all__"
        read_only_fields = ["id", "organization", "created_at", "updated_at"]


class StudyTimepointSerializer(TenantScopedModelSerializer):
    class Meta:
        model = StudyTimepoint
        fields = "__all__"
        read_only_fields = ["id", "organization", "created_at", "updated_at", "status"]


class StabilitySampleSerializer(TenantScopedModelSerializer):
    class Meta:
        model = StabilitySample
        fields = "__all__"
        read_only_fields = ["id", "organization", "created_at", "updated_at", "status"]


class StorageConditionViewSet(StabilityTenantViewSet):
    permission_classes = [StabilityPermissionByAction]
    queryset = StorageCondition.objects.all()
    serializer_class = StorageConditionSerializer


class ProtocolViewSet(StabilityTenantViewSet):
    permission_classes = [StabilityPermissionByAction]
    queryset = Protocol.objects.all()
    serializer_class = ProtocolSerializer


class ProtocolVersionViewSet(StabilityTenantViewSet):
    permission_classes = [StabilityPermissionByAction]
    queryset = ProtocolVersion.objects.all()
    serializer_class = ProtocolVersionSerializer


class SpecificationViewSet(StabilityTenantViewSet):
    permission_classes = [StabilityPermissionByAction]
    queryset = Specification.objects.all()
    serializer_class = SpecificationSerializer


class SpecificationVersionViewSet(StabilityTenantViewSet):
    permission_classes = [StabilityPermissionByAction]
    queryset = SpecificationVersion.objects.all()
    serializer_class = SpecificationVersionSerializer


class StabilityStudyViewSet(StabilityTenantViewSet):
    permission_classes = [StabilityPermissionByAction]
    queryset = StabilityStudy.objects.all()
    serializer_class = StabilityStudySerializer


class StudyBatchViewSet(StabilityTenantViewSet):
    permission_classes = [StabilityPermissionByAction]
    queryset = StudyBatch.objects.all()
    serializer_class = StudyBatchSerializer


class StudyTimepointViewSet(StabilityTenantViewSet):
    permission_classes = [StabilityPermissionByAction]
    queryset = StudyTimepoint.objects.all()
    serializer_class = StudyTimepointSerializer


class StabilitySampleViewSet(StabilityTenantViewSet):
    permission_classes = [StabilityPermissionByAction]
    queryset = StabilitySample.objects.all()
    serializer_class = StabilitySampleSerializer
