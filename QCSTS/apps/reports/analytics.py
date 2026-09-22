from django.db.models import Count
from django.db.models.functions import TruncMonth

from apps.batches.models import Batch
from apps.results.models import TestResult
from apps.schedule.models import TestPoint
from apps.quality.models import OOSInvestigation, OOTInvestigation, Deviation, CAPA, ChangeControl
from core.permissions import IsAnalystOrAbove
from core.responses import success_response
from core.views import TenantScopedAPIView


class AnalyticsView(TenantScopedAPIView):
    permission_classes = [IsAnalystOrAbove]

    def get(self, request):
        org = request.organization

        result_distribution = list(
            TestResult.objects.filter(organization=org, is_active=True)
            .values("pass_fail")
            .annotate(count=Count("id"))
            .order_by("pass_fail")
        )

        batch_distribution = list(
            Batch.objects.filter(organization=org, is_active=True)
            .values("status")
            .annotate(count=Count("id"))
            .order_by("status")
        )

        testpoint_timeline = list(
            TestPoint.objects.filter(organization=org, is_active=True)
            .annotate(scheduled_month=TruncMonth("scheduled_date"))
            .values("scheduled_month", "status")
            .annotate(count=Count("id"))
            .order_by("scheduled_month", "status")
        )

        quality_models = [
            ("oos", OOSInvestigation),
            ("oot", OOTInvestigation),
            ("deviation", Deviation),
            ("capa", CAPA),
            ("change_control", ChangeControl),
        ]
        quality_distribution = []
        for kind, model in quality_models:
            for row in (
                model.objects.filter(organization=org, is_active=True)
                .values("status")
                .annotate(count=Count("id"))
                .order_by("status")
            ):
                quality_distribution.append(
                    {"kind": kind, "status": row["status"], "count": row["count"]}
                )

        return success_response(
            {
                "results": result_distribution,
                "batches": batch_distribution,
                "test_points": [
                    {
                        "month": row["scheduled_month"].date().isoformat() if row["scheduled_month"] else None,
                        "status": row["status"],
                        "count": row["count"],
                    }
                    for row in testpoint_timeline
                ],
                "quality": quality_distribution,
            }
        )
