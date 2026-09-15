from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.platform.services import TenantContextService
from .models import ControlledRecord, ElectronicSignature, ValidationArtifact
from .serializers import ControlledRecordSerializer, ElectronicSignatureSerializer, ValidationArtifactSerializer


class TenantReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return TenantContextService.scope_queryset(self.request, self.queryset)


class ElectronicSignatureViewSet(TenantReadOnlyViewSet):
    queryset = ElectronicSignature.objects.select_related("signer")
    serializer_class = ElectronicSignatureSerializer


class ControlledRecordViewSet(TenantReadOnlyViewSet):
    queryset = ControlledRecord.objects.select_related("locked_by", "approved_by")
    serializer_class = ControlledRecordSerializer


class ValidationArtifactViewSet(TenantReadOnlyViewSet):
    queryset = ValidationArtifact.objects.select_related("approved_by")
    serializer_class = ValidationArtifactSerializer
