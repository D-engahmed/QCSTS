from django.urls import path
from rest_framework.routers import DefaultRouter

from .api import PlanViewSet, SubscriptionViewSet, UsageRecordViewSet
from .paymob_webhooks import PaymobTransactionWebhookView

router = DefaultRouter()
router.register("plans", PlanViewSet, basename="plan")
router.register("subscription", SubscriptionViewSet, basename="subscription")
router.register("usage", UsageRecordViewSet, basename="usage")

urlpatterns = router.urls + [
    path(
        "webhooks/paymob/transaction/",
        PaymobTransactionWebhookView.as_view(),
        name="paymob-transaction-webhook",
    ),
]
