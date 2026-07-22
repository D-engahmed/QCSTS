from rest_framework import serializers
from django.db import transaction

from apps.batches.models import Batch
from apps.schedule.models import TestPoint
from services.schedule_engine import ScheduleEngine
from services.audit_service import AuditService
from core.exceptions import (
    DuplicateBatchNumber,
    MonographNotApproved,
)


class TestPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestPoint
        fields = ["id", "month", "scheduled_date", "status", "completed_at"]
        read_only_fields = fields


class BatchSerializer(serializers.ModelSerializer):
    test_points = TestPointSerializer(many=True, read_only=True)
    product_name = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()

    class Meta:
        model = Batch
        fields = [
            "id",
            "product",
            "product_name",
            "batch_number",
            "mfg_date",
            "expiry_date",
            "incubation_date",
            "study_type",
            "status",
            "shelf",
            "rack",
            "position",
            "location",
            "qty_placed",
            "qty_remaining",
            "test_points",
            "created_at",
        ]
        read_only_fields = ["id", "status", "qty_remaining", "created_at"]

    def get_product_name(self, obj):
        return str(obj.product)

    def get_location(self, obj):
        return obj.get_location()

    def validate_batch_number(self, value):
        if Batch.all_objects.filter(batch_number=value).exists():
            raise DuplicateBatchNumber()
        return value

    def validate(self, data):
        # Rule 1 — incubation_date must be >= mfg_date
        if data.get("incubation_date") and data.get("mfg_date"):
            if data["incubation_date"] < data["mfg_date"]:
                raise serializers.ValidationError(
                    "Incubation date must be on or after manufacturing date."
                )

        # Rule 2 — product must have an approved monograph
        product = data.get("product")
        if product:
            if not product.monograph or not product.monograph.is_approved():
                raise MonographNotApproved()

        # Rule 3 — chamber location must be unique
        shelf = data.get("shelf")
        rack = data.get("rack")
        position = data.get("position")
        if shelf and rack and position:
            if Batch.objects.filter(shelf=shelf, rack=rack, position=position).exists():
                raise serializers.ValidationError("This chamber location is already occupied.")

        return data

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user if request else None

        with transaction.atomic():
            validated_data["qty_remaining"] = validated_data["qty_placed"]
            batch = Batch.objects.create(**validated_data)
            ScheduleEngine.generate(batch, created_by=user)
            AuditService.log(
                performed_by=user,
                action="CREATE",
                model_name="Batch",
                object_id=batch.id,
                object_repr=str(batch),
                new_value={
                    "batch_number": batch.batch_number,
                    "study_type": batch.study_type,
                },
                ip_address=request.META.get("REMOTE_ADDR") if request else None,
            )

        return batch
