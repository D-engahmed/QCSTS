from rest_framework.views import APIView
from rest_framework import status

from apps.batches.models import Batch
from apps.batches.serializers import BatchSerializer
from core.permissions import IsAnalystOrAbove
from core.responses import success_response, error_response
from services.audit_service import AuditService


class BatchListCreateView(APIView):
    serializer_class = BatchSerializer

    """
    GET  /api/v1/batches/  — list all batches
    POST /api/v1/batches/  — create new batch + auto-generate schedule
    """

    permission_classes = [IsAnalystOrAbove]

    def get(self, request):
        queryset = Batch.objects.select_related("product", "product__monograph").all()

        product_id = request.query_params.get("product")
        status_filter = request.query_params.get("status")
        study_type = request.query_params.get("study_type")

        if product_id:
            queryset = queryset.filter(product__id=product_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if study_type:
            queryset = queryset.filter(study_type=study_type)

        return success_response(data=BatchSerializer(queryset, many=True).data)

    def post(self, request):
        serializer = BatchSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        batch = serializer.save(created_by=request.user)
        return success_response(
            data=BatchSerializer(batch).data, status_code=status.HTTP_201_CREATED
        )


class BatchDetailView(APIView):
    serializer_class = BatchSerializer

    """
    GET   /api/v1/batches/<id>/  — batch detail with test points
    PATCH /api/v1/batches/<id>/  — update batch status
    """

    permission_classes = [IsAnalystOrAbove]

    def get_object(self, pk):
        try:
            return Batch.objects.select_related("product", "product__monograph").get(pk=pk)
        except Batch.DoesNotExist:
            return None

    def get(self, request, pk):
        batch = self.get_object(pk)
        if not batch:
            return error_response({"detail": "Batch not found."}, status.HTTP_404_NOT_FOUND)
        return success_response(data=BatchSerializer(batch).data)

    def patch(self, request, pk):
        batch = self.get_object(pk)
        if not batch:
            return error_response({"detail": "Batch not found."}, status.HTTP_404_NOT_FOUND)
        old_value = {"status": batch.status}
        serializer = BatchSerializer(
            batch, data=request.data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        AuditService.log(
            performed_by=request.user,
            action="UPDATE",
            model_name="Batch",
            object_id=batch.id,
            object_repr=str(batch),
            old_value=old_value,
            new_value={"status": batch.status},
            ip_address=request.META.get("REMOTE_ADDR"),
        )

        return success_response(data=BatchSerializer(batch).data)
