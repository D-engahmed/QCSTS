from core.views import TenantScopedAPIView
from rest_framework import status
from django.db import transaction

from apps.batches.models import Batch
from apps.batches.serializers import BatchSerializer
from apps.chamber.models import SamplePull, LocationHistory
from apps.chamber.serializers import (
    SamplePullSerializer,
    LocationHistorySerializer,
    ChangeBatchLocationSerializer,
)
from core.permissions import IsAnalystOrAbove
from core.responses import success_response
from services.audit_service import AuditService


class ChamberInventoryView(TenantScopedAPIView):
    serializer_class = BatchSerializer
    permission_classes = [IsAnalystOrAbove]

    def get(self, request):
        queryset = self.tenant_qs(Batch.objects.select_related("product", "product__monograph"))

        study_type = request.query_params.get("study_type")
        if study_type:
            queryset = queryset.filter(study_type=study_type)

        return success_response(data=BatchSerializer(queryset, many=True).data)


class SamplePullListCreateView(TenantScopedAPIView):
    serializer_class = SamplePullSerializer
    permission_classes = [IsAnalystOrAbove]

    def get(self, request):
        queryset = self.tenant_qs(SamplePull.objects.select_related("batch", "pulled_by", "test_point"))

        batch_id = request.query_params.get("batch")
        if batch_id:
            queryset = queryset.filter(batch__id=batch_id)

        return success_response(data=SamplePullSerializer(queryset, many=True).data)

    def post(self, request):
        # context is required: SamplePullSerializer scopes its batch/test_point
        # fields to the active organization and raises without it, rather than
        # falling back to validating against every tenant's records.
        serializer = SamplePullSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        sample_pull = serializer.save(pulled_by=request.user, created_by=request.user, organization=request.organization)
        return success_response(
            data=SamplePullSerializer(sample_pull).data,
            status_code=status.HTTP_201_CREATED,
        )


class ChangeBatchLocationView(TenantScopedAPIView):
    serializer_class = ChangeBatchLocationSerializer
    permission_classes = [IsAnalystOrAbove]

    def post(self, request):
        # context is required: the batch field is tenant-scoped and raises
        # without it, rather than resolving against every organization's batches.
        serializer = ChangeBatchLocationSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        batch = serializer.validated_data["batch"]
        new_shelf = serializer.validated_data["new_shelf"]
        new_rack = serializer.validated_data["new_rack"]
        new_position = serializer.validated_data["new_position"]
        reason = serializer.validated_data.get("reason", "")

        with transaction.atomic():
            location_log = LocationHistory.objects.create(
                batch=batch,
                old_shelf=batch.shelf,
                old_rack=batch.rack,
                old_position=batch.position,
                new_shelf=new_shelf,
                new_rack=new_rack,
                new_position=new_position,
                changed_by=request.user,
                reason=reason,
                created_by=request.user,
            )
            batch.shelf = new_shelf
            batch.rack = new_rack
            batch.position = new_position
            batch.save(update_fields=["shelf", "rack", "position", "updated_at"])

            AuditService.log(
                performed_by=request.user,
                action="UPDATE",
                model_name="Batch",
                object_id=batch.id,
                object_repr=str(batch),
                old_value={"location": f"{location_log.old_shelf}/{location_log.old_rack}/{location_log.old_position}"},
                new_value={"location": batch.get_location()},
                ip_address=request.META.get("REMOTE_ADDR"),
            )
        return success_response(
            data=LocationHistorySerializer(location_log).data,
            status_code=status.HTTP_201_CREATED,
        )



class LocationHistoryView(TenantScopedAPIView):
    serializer_class = LocationHistorySerializer

    """
    GET /api/v1/chamber/locations/<batch_id>/
    Returns the full location history for a batch.
    """

    permission_classes = [IsAnalystOrAbove]

    def get(self, request, pk):
        history = self.tenant_qs(LocationHistory.objects.select_related("batch").filter(
                batch__organization=request.organization
            ),
        )
        history = history.filter(batch__id=pk)
        return success_response(data=LocationHistorySerializer(history, many=True).data)
