import csv
from django.http import HttpResponse
from django.utils import timezone
from core.views import TenantScopedAPIView
from apps.batches.models import Batch
from apps.products.models import Product
from apps.schedule.models import TestPoint
from apps.results.models import TestResult
from apps.quality.models import OOSInvestigation, OOTInvestigation, Deviation, CAPA, ChangeControl
from core.permissions import IsAnalystOrAbove
from core.responses import success_response


class DashboardView(TenantScopedAPIView):
    permission_classes = [IsAnalystOrAbove]

    def get(self, request):
        today = timezone.localdate()
        in_30_days = today + timezone.timedelta(days=30)
        org = request.organization
        products = Product.objects.filter(organization=org, is_active=True)
        batches = Batch.objects.filter(organization=org, is_active=True)
        test_points = TestPoint.objects.filter(organization=org, is_active=True)
        results = TestResult.objects.filter(organization=org, is_active=True)
        quality = {
            "oos_open": OOSInvestigation.objects.filter(organization=org, status__in=["open", "investigation", "pending_approval"]).count(),
            "oot_open": OOTInvestigation.objects.filter(organization=org, status__in=["open", "investigation", "pending_approval"]).count(),
            "deviations_open": Deviation.objects.filter(organization=org, status__in=["open", "investigation", "pending_approval"]).count(),
            "capa_open": CAPA.objects.filter(organization=org, status__in=["open", "investigation", "pending_approval"]).count(),
            "change_controls_open": ChangeControl.objects.filter(organization=org, status__in=["open", "investigation", "pending_approval"]).count(),
        }
        return success_response({
            "summary": {
                "total_products": products.count(),
                "active_batches": batches.filter(status="active").count(),
                "completed_batches": batches.filter(status="complete").count(),
                "failed_batches": batches.filter(status="failed").count(),
                "total_test_points": test_points.count(),
                "overdue_tests": test_points.filter(status="overdue").count(),
                "upcoming_tests": test_points.filter(status="pending", scheduled_date__gte=today, scheduled_date__lte=in_30_days).count(),
                "submitted_results": results.count(),
                "approved_results": sum(1 for r in results if r.workflow_state() == "approved"),
            },
            "quality": quality,
            "overdue_test_points": [
                {
                    "id": str(tp.id),
                    "batch_number": tp.batch.batch_number,
                    "product_name": tp.batch.product.name,
                    "month": tp.month,
                    "scheduled_date": tp.scheduled_date.isoformat(),
                    "status": tp.status,
                }
                for tp in test_points.filter(status="overdue").select_related("batch", "batch__product")[:50]
            ],
            "upcoming_test_points": [
                {
                    "id": str(tp.id),
                    "batch_number": tp.batch.batch_number,
                    "product_name": tp.batch.product.name,
                    "month": tp.month,
                    "scheduled_date": tp.scheduled_date.isoformat(),
                    "status": tp.status,
                }
                for tp in test_points.filter(
                    status="pending",
                    scheduled_date__gte=today,
                    scheduled_date__lte=in_30_days,
                ).select_related("batch", "batch__product").order_by("scheduled_date")[:50]
            ],
            "active_batches": [
                {
                    "id": str(batch.id),
                    "batch_number": batch.batch_number,
                    "product_name": batch.product.name,
                    "study_type": batch.study_type,
                    "location": batch.get_location(),
                    "qty_remaining": batch.qty_remaining,
                }
                for batch in batches.filter(status="active").select_related("product").order_by("-created_at")[:50]
            ],
        })


class CSVExportView(TenantScopedAPIView):
    permission_classes = [IsAnalystOrAbove]

    def get(self, request):
        resource = request.query_params.get("resource", "results").strip().lower()
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = f'attachment; filename="qcsts-{resource}-{timezone.now().date().isoformat()}.csv"'
        writer = csv.writer(response)
        org = request.organization

        if resource == "results":
            writer.writerow(["id", "test_point", "monograph_test", "value", "unit", "pass_fail", "workflow_state", "analyst", "submitted_at"])
            qs = TestResult.objects.filter(organization=org, is_active=True).select_related("analyst")
            for row in qs.iterator():
                writer.writerow([row.id, row.test_point_id, row.monograph_test_id, row.value, row.unit, row.pass_fail, row.workflow_state(), row.analyst.email if row.analyst else "", row.submitted_at.isoformat() if row.submitted_at else ""])
        elif resource == "batches":
            writer.writerow(["id", "batch_number", "product", "study_type", "status", "location", "qty_placed", "qty_remaining"])
            qs = Batch.objects.filter(organization=org, is_active=True).select_related("product")
            for row in qs.iterator():
                writer.writerow([row.id, row.batch_number, row.product.name, row.study_type, row.status, row.get_location(), row.qty_placed, row.qty_remaining])
        elif resource == "test-points":
            writer.writerow(["id", "batch", "month", "scheduled_date", "status", "completed_at"])
            qs = TestPoint.objects.filter(organization=org, is_active=True).select_related("batch")
            for row in qs.iterator():
                writer.writerow([row.id, row.batch.batch_number, row.month, row.scheduled_date, row.status, row.completed_at.isoformat() if row.completed_at else ""])
        elif resource == "quality":
            writer.writerow(["type", "id", "reference", "title", "severity", "status", "owner", "due_at"])
            for model in (OOSInvestigation, OOTInvestigation, Deviation, CAPA, ChangeControl):
                for row in model.objects.filter(organization=org, is_active=True).select_related("owner").iterator():
                    writer.writerow([model.__name__, row.id, row.reference, row.title, row.severity, row.status, row.owner.email if row.owner else "", row.due_at.isoformat() if row.due_at else ""])
        else:
            return success_response({"detail": "Unsupported resource. Use results, batches, test-points, or quality."}, status_code=400)
        return response
