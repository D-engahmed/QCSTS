from rest_framework.routers import DefaultRouter

from apps.stability.api import (
    ProtocolVersionViewSet,
    ProtocolViewSet,
    SpecificationVersionViewSet,
    SpecificationViewSet,
    StabilitySampleViewSet,
    StabilityStudyViewSet,
    StorageConditionViewSet,
    StudyBatchViewSet,
    StudyTimepointViewSet,
)

router = DefaultRouter()
router.register("storage-conditions", StorageConditionViewSet, basename="stability-storage-condition")
router.register("protocols", ProtocolViewSet, basename="stability-protocol")
router.register("protocol-versions", ProtocolVersionViewSet, basename="stability-protocol-version")
router.register("specifications", SpecificationViewSet, basename="stability-specification")
router.register("specification-versions", SpecificationVersionViewSet, basename="stability-specification-version")
router.register("studies", StabilityStudyViewSet, basename="stability-study")
router.register("study-batches", StudyBatchViewSet, basename="stability-study-batch")
router.register("timepoints", StudyTimepointViewSet, basename="stability-timepoint")
router.register("samples", StabilitySampleViewSet, basename="stability-sample")

urlpatterns = router.urls
