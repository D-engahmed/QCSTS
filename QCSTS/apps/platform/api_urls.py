from rest_framework.routers import DefaultRouter
from .api import OrganizationViewSet, SiteViewSet

router = DefaultRouter()
router.register("organizations", OrganizationViewSet, basename="organization")
router.register("sites", SiteViewSet, basename="site")
urlpatterns = router.urls
