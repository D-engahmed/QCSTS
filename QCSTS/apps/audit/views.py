from rest_framework.views import APIView
from rest_framework import status

from apps.audit.models import AuditLog
from apps.audit.serializers import AuditLogSerializer
from core.permissions import IsQAManager
from core.responses import success_response


class AuditLogListView(APIView):
    serializer_class = AuditLogSerializer

    """
    GET /api/v1/audit/
    Returns the full audit trail. QA Manager and Admin only.

    Supports filtering via query params:
        ?model_name=Batch
        ?action=UPDATE
        ?performed_by=<user_id>
        ?date_from=2024-01-01
        ?date_to=2024-12-31
    """

    permission_classes = [IsQAManager]

    def get(self, request):
        queryset = AuditLog.objects.all()

        model_name = request.query_params.get("model_name")
        action = request.query_params.get("action")
        performed_by = request.query_params.get("performed_by")
        date_from = request.query_params.get("date_from")
        date_to = request.query_params.get("date_to")

        if model_name:
            queryset = queryset.filter(model_name=model_name)
        if action:
            queryset = queryset.filter(action=action)
        if performed_by:
            queryset = queryset.filter(performed_by__id=performed_by)
        if date_from:
            queryset = queryset.filter(timestamp__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(timestamp__date__lte=date_to)

        serializer = AuditLogSerializer(queryset, many=True)
        return success_response(data=serializer.data)


class AuditLogDetailView(APIView):
    serializer_class = AuditLogSerializer

    """
    GET /api/v1/audit/<id>/
    Returns a single audit log entry. QA Manager and Admin only.
    """

    permission_classes = [IsQAManager]

    def get(self, request, pk):
        try:
            log = AuditLog.objects.get(pk=pk)
        except AuditLog.DoesNotExist:
            from core.responses import error_response

            return error_response(
                {"detail": "Audit log entry not found."}, status.HTTP_404_NOT_FOUND
            )
        return success_response(data=AuditLogSerializer(log).data)
