from rest_framework.routers import DefaultRouter
from .api import PlanViewSet, SubscriptionViewSet, UsageRecordViewSet

router = DefaultRouter()
router.register("plans", PlanViewSet, basename="plan")
router.register("subscription", SubscriptionViewSet, basename="subscription")
router.register("usage", UsageRecordViewSet, basename="usage")
urlpatterns = router.urls
