from rest_framework.routers import DefaultRouter
from .views import ElectronicSignatureViewSet, ValidationArtifactViewSet

router = DefaultRouter()
router.register("signatures", ElectronicSignatureViewSet, basename="signature")
router.register("validation", ValidationArtifactViewSet, basename="validation-artifact")
urlpatterns = router.urls
