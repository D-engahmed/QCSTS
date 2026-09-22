from rest_framework import serializers
from apps.chamber.models import SamplePull, LocationHistory
from apps.batches.models import Batch
from apps.schedule.models import TestPoint
from core.exceptions import InsufficientQuantity
from core.serializers import TenantScopedModelSerializer, TenantScopedPrimaryKeyRelatedField


class SamplePullSerializer(TenantScopedModelSerializer):
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

    def get_batch_number(self, obj) -> str:
        return obj.batch.batch_number

    def validate(self, data):
        batch = data.get("batch")
        qty_pulled = data.get("qty_pulled")
        test_point = data.get("test_point")

        if qty_pulled is None or qty_pulled <= 0:
            raise serializers.ValidationError({"qty_pulled": "Pull quantity must be greater than zero."})

        if batch and qty_pulled > batch.qty_remaining:
            raise InsufficientQuantity(
                f"Cannot pull {qty_pulled}. Only {batch.qty_remaining} remaining."
            )

        if batch and test_point and test_point.batch_id != batch.id:
            raise serializers.ValidationError(
                {"test_point": "The selected test point does not belong to the selected batch."}
            )

        return data

    def create(self, validated_data):
        from django.db import transaction

        with transaction.atomic():
            batch_id = validated_data["batch"].pk
            batch = Batch.objects.select_for_update().get(
                pk=batch_id,
                organization=validated_data["batch"].organization,
                is_active=True,
            )
            qty_pulled = validated_data["qty_pulled"]
            test_point = validated_data.get("test_point")

            # Re-check after acquiring the row lock. The serializer-level
            # validation alone is not safe against concurrent sample pulls.
            if qty_pulled > batch.qty_remaining:
                raise InsufficientQuantity(
                    f"Cannot pull {qty_pulled}. Only {batch.qty_remaining} remaining."
                )

            batch.qty_remaining -= qty_pulled
            batch.save(update_fields=["qty_remaining", "updated_at"])

            validated_data["batch"] = batch
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
            "batch",
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

    ``batch`` was previously ``PrimaryKeyRelatedField(queryset=Batch.objects.all())``
    with no organization filter — any authenticated analyst could submit
    another tenant's batch ID and this endpoint would relocate it and log the
    move under the wrong organization's audit trail. Requires
    context={"request": request} to be passed to this serializer.
    """

    batch = TenantScopedPrimaryKeyRelatedField(queryset=Batch.objects.all())
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
                organization=batch.organization,
                shelf=new_shelf,
                rack=new_rack,
                position=new_position,
                is_active=True,
            )
            .exclude(id=batch.id)
            .exists()
        ):
            raise serializers.ValidationError("This chamber location is already occupied.")
        return data