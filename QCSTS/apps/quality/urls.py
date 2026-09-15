from rest_framework.routers import DefaultRouter
from .views import CAPAViewSet, ChangeControlViewSet, DeviationViewSet, OOSInvestigationViewSet, OOTInvestigationViewSet

router = DefaultRouter()
router.register("oos", OOSInvestigationViewSet, basename="oos")
router.register("oot", OOTInvestigationViewSet, basename="oot")
router.register("deviations", DeviationViewSet, basename="deviation")
router.register("capa", CAPAViewSet, basename="capa")
router.register("change-control", ChangeControlViewSet, basename="change-control")
urlpatterns = router.urls
