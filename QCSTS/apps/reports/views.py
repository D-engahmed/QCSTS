from django.utils import timezone
from rest_framework.views import APIView

from apps.batches.models import Batch
from apps.products.models import Product
from apps.schedule.models import TestPoint
from core.permissions import IsAnalystOrAbove
from core.responses import success_response


class DashboardView(APIView):
    serializer_class = None
    permission_classes = [IsAnalystOrAbove]

    def get(self, request):
        today = timezone.now().date()
        in_30_days = today + timezone.timedelta(days=30)

        total_products = Product.objects.filter(is_active=True).count()
        active_batches = Batch.objects.filter(status="active").count()
        overdue_count = TestPoint.objects.filter(status="overdue").count()
        upcoming_count = TestPoint.objects.filter(
            status="pending",
            scheduled_date__gte=today,
            scheduled_date__lte=in_30_days,
        ).count()

        # Overdue test points – include product_name and batch_number
        overdue_points = TestPoint.objects.filter(status="overdue").select_related("batch", "batch__product")[:20]
        overdue_data = []
        for tp in overdue_points:
            overdue_data.append({
                "id": str(tp.id),
                "batch_number": tp.batch.batch_number,
                "product_name": tp.batch.product.name,
                "month": tp.month,
                "scheduled_date": tp.scheduled_date.isoformat(),
                "status": tp.status,
            })

        # Upcoming test points
        upcoming_points = TestPoint.objects.filter(
            status="pending",
            scheduled_date__gte=today,
            scheduled_date__lte=in_30_days,
        ).select_related("batch", "batch__product")[:20]
        upcoming_data = []
        for tp in upcoming_points:
            upcoming_data.append({
                "id": str(tp.id),
                "batch_number": tp.batch.batch_number,
                "product_name": tp.batch.product.name,
                "month": tp.month,
                "scheduled_date": tp.scheduled_date.isoformat(),
                "status": tp.status,
            })

        # Failed batches
        failed_batches = Batch.objects.filter(status="failed").select_related("product")[:10]
        failed_data = []
        for b in failed_batches:
            failed_data.append({
                "id": str(b.id),
                "batch_number": b.batch_number,
                "product_name": b.product.name,
                "study_type": b.study_type,
                "status": b.status,
            })

        # Active batches in chamber
        active_batches_list = Batch.objects.filter(status="active").select_related("product")[:10]
        active_data = []
        for b in active_batches_list:
            active_data.append({
                "id": str(b.id),
                "batch_number": b.batch_number,
                "product_name": b.product.name,
                "study_type": b.study_type,
                "location": b.get_location(),
                "qty_remaining": b.qty_remaining,
            })

        return success_response({
            "summary": {
                "total_products": total_products,
                "active_batches": active_batches,
                "overdue_tests": overdue_count,
                "upcoming_tests": upcoming_count,
            },
            "overdue_test_points": overdue_data,
            "upcoming_test_points": upcoming_data,
            "failed_batches": failed_data,
            "active_batches": active_data,
        })