from rest_framework.routers import DefaultRouter
from .views import ControlledRecordViewSet, ElectronicSignatureViewSet, ValidationArtifactViewSet

router = DefaultRouter()
router.register("signatures", ElectronicSignatureViewSet, basename="signature")
router.register("records", ControlledRecordViewSet, basename="controlled-record")
router.register("validation", ValidationArtifactViewSet, basename="validation-artifact")
urlpatterns = router.urls
