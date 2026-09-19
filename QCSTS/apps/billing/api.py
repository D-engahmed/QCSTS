from rest_framework import serializers
from apps.platform.permissions import HasTenantContext
from core.views import TenantScopedViewSet, TenantExemptViewSet
from .models import Plan, Subscription, UsageRecord


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class SubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)

    class Meta:
        model = Subscription
        fields = "__all__"
        read_only_fields = "__all__"


class UsageRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsageRecord
        fields = "__all__"
        read_only_fields = "__all__"


class PlanViewSet(TenantExemptViewSet):
    """Plans are global catalog data, not organization-owned records."""

    permission_classes = [HasTenantContext]
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
