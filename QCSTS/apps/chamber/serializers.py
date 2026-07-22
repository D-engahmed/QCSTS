from rest_framework import serializers
from apps.chamber.models import SamplePull, LocationHistory
from apps.batches.models import Batch
from apps.schedule.models import TestPoint
from core.exceptions import InsufficientQuantity


class SamplePullSerializer(serializers.ModelSerializer):
    batch_number = serializers.SerializerMethodField()

    class Meta:
        model = SamplePull
        fields = [
            "id",
            "batch",
            "batch_number",
            "test_point",
            "qty_pulled",
            "pulled_by",
            "pulled_at",
            "notes",
        ]
        read_only_fields = ["id", "pulled_by", "pulled_at"]

    def get_batch_number(self, obj):
        return obj.batch.batch_number

    def validate(self, data):
        batch = data.get("batch")
        qty_pulled = data.get("qty_pulled")

        if batch and qty_pulled:
            if qty_pulled > batch.qty_remaining:
                raise InsufficientQuantity(
                    f"Cannot pull {qty_pulled}. Only {batch.qty_remaining} remaining."
                )
        return data

    def create(self, validated_data):
        from django.db import transaction

        with transaction.atomic():
            batch = validated_data["batch"]
            qty_pulled = validated_data["qty_pulled"]
            test_point = validated_data.get("test_point")

            # Reduce qty_remaining on the batch
            batch.qty_remaining -= qty_pulled
            batch.save(update_fields=["qty_remaining", "updated_at"])

            pull = SamplePull.objects.create(**validated_data)

            # --- NEW LOGIC: Update TestPoint status to "pulled" ---
            if test_point and test_point.status not in ["completed", "failed", "pulled"]:
                test_point.status = "pulled"
                test_point.save(update_fields=["status"])

            return pull


class LocationHistorySerializer(serializers.ModelSerializer):
    batch_number = serializers.SerializerMethodField()

    class Meta:
        model = LocationHistory
        fields = [
            "id",
            "batch",
            "batch_number",
            "old_shelf",
            "old_rack",
            "old_position",
            "new_shelf",
            "new_rack",
            "new_position",
            "changed_by",
            "reason",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "changed_by",
            "created_at",
            "old_shelf",
            "old_rack",
            "old_position",
        ]

    def get_batch_number(self, obj):
        return obj.batch.batch_number


class ChangeBatchLocationSerializer(serializers.Serializer):
    """
    Used when an analyst moves a batch to a new location in the chamber.
    """

    batch = serializers.PrimaryKeyRelatedField(queryset=Batch.objects.all())
    new_shelf = serializers.CharField(max_length=50)
    new_rack = serializers.CharField(max_length=50)
    new_position = serializers.CharField(max_length=50)
    reason = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        batch = data.get("batch")
        new_shelf = data.get("new_shelf")
        new_rack = data.get("new_rack")
        new_position = data.get("new_position")

        # Check new location is not already occupied
        if (
            Batch.objects.filter(
                shelf=new_shelf,
                rack=new_rack,
                position=new_position,
            )
            .exclude(id=batch.id)
            .exists()
        ):
            raise serializers.ValidationError("This chamber location is already occupied.")
        return data