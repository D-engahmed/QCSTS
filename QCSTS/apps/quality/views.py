from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.platform.services import TenantContextService
from .models import CAPA, ChangeControl, Deviation, OOSInvestigation, OOTInvestigation
from .serializers import CAPASerializer, ChangeControlSerializer, DeviationSerializer, OOSInvestigationSerializer, OOTInvestigationSerializer


class TenantScopedViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return TenantContextService.scope_queryset(self.request, self.queryset)
    def perform_create(self, serializer):
        TenantContextService.resolve(self.request)
        serializer.save(organization=self.request.organization)


class OOSInvestigationViewSet(TenantScopedViewSet):
    queryset = OOSInvestigation.objects.select_related("result", "owner")
    serializer_class = OOSInvestigationSerializer


class OOTInvestigationViewSet(TenantScopedViewSet):
    queryset = OOTInvestigation.objects.select_related("result", "owner")
    serializer_class = OOTInvestigationSerializer


class DeviationViewSet(TenantScopedViewSet):
    queryset = Deviation.objects.select_related("owner")
    serializer_class = DeviationSerializer


class CAPAViewSet(TenantScopedViewSet):
    queryset = CAPA.objects.select_related("owner")
    serializer_class = CAPASerializer


class ChangeControlViewSet(TenantScopedViewSet):
    queryset = ChangeControl.objects.select_related("owner")
    serializer_class = ChangeControlSerializer
