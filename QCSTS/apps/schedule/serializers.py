from rest_framework import serializers
from apps.schedule.models import TestPoint


class TestPointSerializer(serializers.ModelSerializer):
    batch_number = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()

    class Meta:
        model = TestPoint
        fields = [
            "id",
            "batch",
            "batch_number",
            "product_name",
            "month",
            "scheduled_date",
            "status",
            "completed_at",
            "created_at",
        ]
        read_only_fields = fields

    def get_batch_number(self, obj):
        return obj.batch.batch_number

    def get_product_name(self, obj):
        return obj.batch.product.name
