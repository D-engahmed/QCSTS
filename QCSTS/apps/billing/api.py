from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAuthenticated
from apps.platform.services import TenantContextService
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


class TenantReadOnly(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return TenantContextService.scope_queryset(self.request, self.queryset)


class PlanViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = PlanSerializer
    queryset = Plan.objects.filter(active=True)


class SubscriptionViewSet(TenantReadOnly):
    serializer_class = SubscriptionSerializer
    queryset = Subscription.objects.select_related("plan")


class UsageRecordViewSet(TenantReadOnly):
    serializer_class = UsageRecordSerializer
    queryset = UsageRecord.objects.all()
