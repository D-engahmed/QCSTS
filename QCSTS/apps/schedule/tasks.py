import logging
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task
def mark_overdue_test_points():
    """
    Runs every day at 06:00 AM via Celery Beat.
    Finds all pending or overdue test points whose scheduled_date has passed,
    marks them overdue, then updates parent batch statuses.

    EXCLUDES test points with status "pulled" to prevent breaking the workflow.
    """
    from apps.schedule.models import TestPoint

    today = timezone.now().date()

    # Only target pending or overdue statuses. EXCLUDE "pulled".
    overdue_qs = TestPoint.objects.filter(
        status__in=["pending", "overdue"],
        scheduled_date__lt=today,
    )

    count = overdue_qs.count()

    if count > 0:
        # Collect affected batch IDs before the bulk update
        affected_batch_ids = list(
            overdue_qs.values_list("batch_id", flat=True).distinct()
        )

        overdue_qs.update(status="overdue")

        # Now recalculate status for every affected batch
        from apps.batches.models import Batch

        for batch_id in affected_batch_ids:
            try:
                batch = Batch.objects.get(pk=batch_id)
                batch.update_status_from_test_points()
            except Batch.DoesNotExist:
                pass

        logger.info("mark_overdue_test_points: marked %d test points as overdue", count)
    else:
        logger.info("mark_overdue_test_points: no overdue test points found")

    return count