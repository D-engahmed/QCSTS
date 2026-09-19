from core.views import TenantScopedModelViewSet
from .models import CAPA, ChangeControl, Deviation, OOSInvestigation, OOTInvestigation
from .serializers import CAPASerializer, ChangeControlSerializer, DeviationSerializer, OOSInvestigationSerializer, OOTInvestigationSerializer
from apps.platform.permissions import HasTenantContext


class QualityTenantViewSet(TenantScopedModelViewSet):
    permission_classes = [HasTenantContext]


class OOSInvestigationViewSet(QualityTenantViewSet):
    permission_classes = [HasTenantContext]
    queryset = OOSInvestigation.objects.select_related("result", "owner")
    serializer_class = OOSInvestigationSerializer


class OOTInvestigationViewSet(QualityTenantViewSet):
    permission_classes = [HasTenantContext]
    queryset = OOTInvestigation.objects.select_related("result", "owner")
    serializer_class = OOTInvestigationSerializer


class DeviationViewSet(QualityTenantViewSet):
    permission_classes = [HasTenantContext]
    queryset = Deviation.objects.select_related("owner")
    serializer_class = DeviationSerializer


class CAPAViewSet(QualityTenantViewSet):
    permission_classes = [HasTenantContext]
    queryset = CAPA.objects.select_related("owner")
    serializer_class = CAPASerializer


class ChangeControlViewSet(QualityTenantViewSet):
    permission_classes = [HasTenantContext]
    queryset = ChangeControl.objects.select_related("owner")
    serializer_class = ChangeControlSerializer
