from core.views import TenantScopedModelViewSet
from .models import CAPA, ChangeControl, Deviation, OOSInvestigation, OOTInvestigation
from .serializers import CAPASerializer, ChangeControlSerializer, DeviationSerializer, OOSInvestigationSerializer, OOTInvestigationSerializer
from apps.platform.permissions import HasTenantContext


class QualityTenantViewSet(TenantScopedModelViewSet):
    permission_classes = [HasTenantContext]


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
