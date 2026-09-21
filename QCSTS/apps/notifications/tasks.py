import logging

from celery import shared_task
from django.utils import timezone
from django.db import transaction

from apps.notifications.models import Notification
from apps.notifications.services import create_notification

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def notify_upcoming_and_overdue_test_points(self):
    from apps.schedule.models import TestPoint
    from apps.platform.models import Membership

    today = timezone.localdate()
    upcoming = today + timezone.timedelta(days=1)

    try:
        with transaction.atomic():
            points = list(
                TestPoint.objects.filter(
                    status="pending",
                    scheduled_date__lte=upcoming,
                    scheduled_date__gte=today,
                ).select_related("batch", "batch__organization")
            )
            overdue = list(
                TestPoint.objects.filter(
                    status="overdue",
                ).select_related("batch", "batch__organization")
            )
            count = 0
            for point in points:
                memberships = Membership.objects.filter(
                    organization=point.organization,
                    is_active=True,
                    role__name__in=["supervisor", "qa_manager", "admin"],
                ).select_related("user")
                for membership in memberships:
                    if Notification.objects.filter(
                        organization=point.organization,
                        user=membership.user,
                        kind=Notification.Kind.OVERDUE,
                        body__contains=str(point.id),
                        created_at__date=today,
                    ).exists():
                        continue
                    create_notification(
                        user=membership.user,
                        organization=point.organization,
                        title=f"Test point due: Month {point.month}",
                        body=f"QCSTS test point {point.id} for batch {point.batch.batch_number} is due by {point.scheduled_date}.",
                        kind=Notification.Kind.OVERDUE,
                        severity=Notification.Severity.WARNING,
                        action_url="/app/batches",
                    )
                    count += 1
            for point in overdue[:500]:
                memberships = Membership.objects.filter(
                    organization=point.organization,
                    is_active=True,
                    role__name__in=["supervisor", "qa_manager", "admin"],
                ).select_related("user")
                for membership in memberships:
                    if Notification.objects.filter(
                        organization=point.organization,
                        user=membership.user,
                        kind=Notification.Kind.OVERDUE,
                        body__contains=str(point.id),
                        created_at__date=today,
                    ).exists():
                        continue
                    create_notification(
                        user=membership.user,
                        organization=point.organization,
                        title=f"Overdue test point: Month {point.month}",
                        body=f"QCSTS test point {point.id} for batch {point.batch.batch_number} is overdue since {point.scheduled_date}.",
                        kind=Notification.Kind.OVERDUE,
                        severity=Notification.Severity.CRITICAL,
                        action_url="/app/batches",
                    )
                    count += 1
            return count
    except Exception as exc:
        logger.exception("Notification sweep failed")
        raise self.retry(exc=exc)
