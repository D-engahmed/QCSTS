from rest_framework.views import APIView
from rest_framework import status
from django.utils import timezone

from apps.schedule.models import TestPoint
from apps.schedule.serializers import TestPointSerializer
from core.permissions import IsAnalystOrAbove
from core.responses import success_response, error_response


class TestPointListView(APIView):
    serializer_class = TestPointSerializer

    """
    GET /api/v1/test-points/
    List test points with optional filters.

    Query params:
        ?batch=<batch_id>
        ?status=pending|overdue|completed|failed
        ?upcoming=true  — due in next 30 days
    """

    permission_classes = [IsAnalystOrAbove]

    def get(self, request):
        queryset = TestPoint.objects.select_related("batch", "batch__product").all()

        batch_id = request.query_params.get("batch")
        status_filter = request.query_params.get("status")
        upcoming = request.query_params.get("upcoming")

        if batch_id:
            queryset = queryset.filter(batch__id=batch_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if upcoming == "true":
            today = timezone.now().date()
            in_30_days = today + timezone.timedelta(days=30)
            queryset = queryset.filter(
                scheduled_date__gte=today, scheduled_date__lte=in_30_days, status="pending"
            )

        return success_response(data=TestPointSerializer(queryset, many=True).data)


class TestPointDetailView(APIView):
    serializer_class = TestPointSerializer

    """
    GET /api/v1/test-points/<id>/
    Get a single test point with full details.
    """

    permission_classes = [IsAnalystOrAbove]

    def get(self, request, pk):
        try:
            tp = TestPoint.objects.select_related("batch", "batch__product").get(pk=pk)
        except TestPoint.DoesNotExist:
            return error_response({"detail": "Test point not found."}, status.HTTP_404_NOT_FOUND)
        return success_response(data=TestPointSerializer(tp).data)
