from core.views import TenantScopedViewSet
from apps.platform.permissions import HasTenantContext
from .models import ControlledRecord, ElectronicSignature, ValidationArtifact
from .serializers import ControlledRecordSerializer, ElectronicSignatureSerializer, ValidationArtifactSerializer


class ComplianceTenantViewSet(TenantScopedViewSet):
    permission_classes = [HasTenantContext]


class ElectronicSignatureViewSet(ComplianceTenantViewSet):
    queryset = ElectronicSignature.objects.select_related("signer")
    serializer_class = ElectronicSignatureSerializer


class ControlledRecordViewSet(ComplianceTenantViewSet):
    queryset = ControlledRecord.objects.select_related("locked_by", "approved_by")
    serializer_class = ControlledRecordSerializer


class ValidationArtifactViewSet(ComplianceTenantViewSet):
    queryset = ValidationArtifact.objects.select_related("approved_by")
    serializer_class = ValidationArtifactSerializer
