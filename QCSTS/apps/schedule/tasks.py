import logging
from celery import shared_task
from django.utils import timezone
from django.db import transaction

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def mark_overdue_test_points(self):
    """
    Runs every day at 06:00 AM via Celery Beat.
    Finds all pending or overdue test points whose scheduled_date has passed,
    marks them overdue, then updates parent batch statuses.
    
    Tenant-aware: Logs organization context for observability.
    Idempotent: Safe to retry if interrupted.
    """
    from apps.schedule.models import TestPoint

    today = timezone.now().date()

    # Only target pending or overdue statuses. EXCLUDE "pulled".
    overdue_qs = TestPoint.objects.filter(
        status__in=["pending", "overdue"],
        scheduled_date__lt=today,
    ).select_related("batch", "batch__organization")

    # Evaluate queryset to get batch instances BEFORE updating to avoid N+1 queries
    affected_test_points = list(overdue_qs)
    
    if not affected_test_points:
        logger.info("mark_overdue_test_points: no overdue test points found")
        return 0

    # Deduplicate batches
    batches_to_update = {tp.batch_id: tp.batch for tp in affected_test_points}
    tp_ids = [tp.id for tp in affected_test_points]

    try:
        with transaction.atomic():
            # Bulk update test points
            updated_count = TestPoint.objects.filter(id__in=tp_ids).update(status="overdue")
            logger.info("mark_overdue_test_points: marked %d test points as overdue", updated_count)
            
            # Recalculate status for every affected batch
            for batch_id, batch in batches_to_update.items():
                try:
                    # Pass triggered_by=None to indicate system/automated action
                    batch.update_status_from_test_points(triggered_by=None)
                except Exception as e:
                    # Log the error with TENANT CONTEXT but don't crash the whole task
                    org_name = batch.organization.name if batch.organization else "Unknown"
                    logger.error(
                        "mark_overdue_test_points: failed to update batch %s (Org: %s) | error: %s",
                        batch.batch_number,
                        org_name,
                        str(e)
                    )
                    
    except Exception as exc:
        # Retry the task if the database transaction fails entirely
        logger.error("mark_overdue_test_points: transaction failed, scheduling retry | error: %s", str(exc))
        raise self.retry(exc=exc)

    return len(affected_test_points)