from rest_framework import serializers
from apps.platform.permissions import HasTenantContext
from rest_framework.permissions import IsAuthenticated
from core.views import TenantScopedViewSet, TenantExemptViewSet
from .models import Plan, Subscription, UsageRecord


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = "__all__"
        read_only_fields = ("id", "code", "name", "description", "monthly_price", "annual_price", "currency", "max_users", "max_sites", "max_studies", "max_storage_mb", "api_access", "active", "created_at", "updated_at")


class SubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)

    class Meta:
        model = Subscription
        fields = "__all__"
        read_only_fields = ("id", "organization", "plan", "status", "interval", "provider", "provider_subscription_id", "trial_ends_at", "current_period_start", "current_period_end", "cancel_at_period_end", "canceled_at", "created_at", "updated_at")


class UsageRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsageRecord
        fields = "__all__"
        read_only_fields = ("id", "organization", "metric", "period_start", "period_end", "quantity", "created_at")


class PlanViewSet(TenantExemptViewSet):
    """Plans are global catalog data, not organization-owned records."""

    permission_classes = [IsAuthenticated]
    serializer_class = PlanSerializer
    queryset = Plan.objects.filter(active=True)


class SubscriptionViewSet(TenantScopedViewSet):
    permission_classes = [HasTenantContext]
    serializer_class = SubscriptionSerializer
    queryset = Subscription.objects.select_related("plan")


class UsageRecordViewSet(TenantScopedViewSet):
    permission_classes = [HasTenantContext]
    serializer_class = UsageRecordSerializer
    queryset = UsageRecord.objects.all()
