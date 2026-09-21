from django.db import transaction
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from core.views import TenantScopedModelViewSet
from core.permissions import IsAnalystOrAbove, IsReviewerOrAbove, IsQAManager
from apps.compliance.models import ElectronicSignature
from services.signature_service import SignatureService
from services.audit_service import AuditService
from .models import CAPA, ChangeControl, Deviation, OOSInvestigation, OOTInvestigation
from .serializers import CAPASerializer, ChangeControlSerializer, DeviationSerializer, OOSInvestigationSerializer, OOTInvestigationSerializer


class QualityTenantViewSet(TenantScopedModelViewSet):
    permission_classes = []
    """
    Controlled quality-event API.

    CRUD is intentionally restricted to creation/read/update of descriptive
    fields; lifecycle state changes go through /transition/ so every state
    change is validated, audited, and (for approval/closure) electronically
    signed.
    """

    transition_permissions = {
        "open": IsAnalystOrAbove,
        "investigation": IsAnalystOrAbove,
        "pending_approval": IsReviewerOrAbove,
        "approved": IsQAManager,
        "closed": IsQAManager,
        "canceled": IsQAManager,
    }

    def get_permissions(self):
        if getattr(self, "action", None) in {"list", "retrieve", "create"}:
            return [IsAnalystOrAbove()]
        if getattr(self, "action", None) in {"update", "partial_update"}:
            return [IsReviewerOrAbove()]
        if getattr(self, "action", None) == "destroy":
            return [IsQAManager()]
        if getattr(self, "action", None) == "transition":
            requested = getattr(self.request, "data", {}).get("status")
            permission = self.transition_permissions.get(requested, IsQAManager)
            return [permission()]
        return [IsAnalystOrAbove()]

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.organization,
            created_by=self.request.user,
            owner=self.request.user,
        )

    @action(detail=True, methods=["post"], url_path="transition")
    @transaction.atomic
    def transition(self, request, pk=None):
        event = self.get_object()
        target = (request.data.get("status") or "").strip().lower()
        comments = (request.data.get("comments") or "").strip()
        allowed = {
            "open": {"investigation", "canceled"},
            "investigation": {"pending_approval", "canceled"},
            "pending_approval": {"approved", "investigation"},
            "approved": {"closed"},
            "closed": set(),
            "canceled": set(),
        }
        current = event.status
        if target not in allowed.get(current, set()):
            return Response(
                {"detail": f"Invalid transition from {current} to {target}."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if target in {"investigation", "pending_approval", "approved", "closed", "canceled"} and not comments:
            return Response({"detail": "Transition comments are required."}, status=status.HTTP_400_BAD_REQUEST)

        if target in {"approved", "closed"}:
            token = request.headers.get("X-Signature-Token")
            if not token or not SignatureService.validate(request.user, token):
                return Response({"detail": "Valid electronic signature authentication is required."}, status=403)

        old_status = event.status
        event.status = target
        if target == "closed":
            event.closed_at = timezone.now()
        event.save(update_fields=["status", "closed_at", "updated_at"] if hasattr(event, "closed_at") else ["status", "updated_at"])

        if target in {"approved", "closed"}:
            meaning = (
                ElectronicSignature.Meaning.APPROVAL
                if target == "approved"
                else ElectronicSignature.Meaning.CLOSURE
            )
            ElectronicSignature.issue(
                organization=request.organization,
                signer=request.user,
                record_type=event.__class__.__name__,
                record_id=event.id,
                record_version=str(event.updated_at.timestamp()),
                meaning=meaning,
                reason=comments,
                authentication_secret=__import__("django.conf", fromlist=["settings"]).settings.SECRET_KEY,
            )

        AuditService.log(
            performed_by=request.user,
            action="APPROVE" if target == "approved" else "UPDATE",
            model_name=event.__class__.__name__,
            object_id=event.id,
            object_repr=str(event),
            old_value={"status": old_status},
            new_value={"status": target, "comments": comments},
            ip_address=request.META.get("REMOTE_ADDR"),
            notes="Controlled quality-event lifecycle transition.",
            organization=request.organization,
        )
        return Response(self.get_serializer(event).data, status=status.HTTP_200_OK)


class OOSInvestigationViewSet(QualityTenantViewSet):
    queryset = OOSInvestigation.objects.select_related("result", "owner")
    serializer_class = OOSInvestigationSerializer


class OOTInvestigationViewSet(QualityTenantViewSet):
    queryset = OOTInvestigation.objects.select_related("result", "owner")
    serializer_class = OOTInvestigationSerializer


class DeviationViewSet(QualityTenantViewSet):
    queryset = Deviation.objects.select_related("owner")
    serializer_class = DeviationSerializer


class CAPAViewSet(QualityTenantViewSet):
    queryset = CAPA.objects.select_related("owner")
    serializer_class = CAPASerializer


class ChangeControlViewSet(QualityTenantViewSet):
    queryset = ChangeControl.objects.select_related("owner")
    serializer_class = ChangeControlSerializer
