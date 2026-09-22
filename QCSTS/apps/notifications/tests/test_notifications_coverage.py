from datetime import timedelta
from unittest.mock import MagicMock, patch

import pytest
from django.utils import timezone
from rest_framework.test import APIRequestFactory, force_authenticate

from apps.accounts.tests.factories import AdminFactory
from apps.notifications.models import Notification
from apps.notifications.services import create_notification
from apps.notifications.tasks import notify_upcoming_and_overdue_test_points
from apps.notifications.views import NotificationViewSet


@pytest.mark.django_db
def test_create_notification_and_read_actions():
    user = AdminFactory()
    org = user.memberships.select_related("organization").get().organization
    with patch("apps.notifications.services.send_mail") as mail:
        notification = create_notification(
            user=user, organization=org, title="System", body="Body",
            action_url="/app", send_email=True,
        )
        mail.assert_called_once()
    assert notification.organization_id == org.id

    factory = APIRequestFactory()
    request = factory.post("/notifications/read/")
    force_authenticate(request, user=user)
    view = NotificationViewSet()
    view.request = request
    view.get_object = MagicMock(return_value=notification)
    view.get_serializer = MagicMock(return_value=MagicMock(data={"id": str(notification.id)}))
    response = view.read(request, pk=str(notification.id))
    assert response.status_code == 200
    notification.refresh_from_db()
    assert notification.read_at is not None

    unread = Notification.objects.create(
        organization=org, user=user, title="Unread", body="Unread",
    )
    view.get_queryset = MagicMock(return_value=Notification.objects.filter(user=user, organization=org))
    response = view.read_all(request)
    assert response.status_code == 200
    assert response.data["updated"] >= 1
    unread.refresh_from_db()
    assert unread.read_at is not None


@pytest.mark.django_db
def test_notification_sweep_creates_upcoming_and_overdue():
    user = AdminFactory()
    org = user.memberships.select_related("organization").get().organization
    point = MagicMock()
    point.id = "point-1"
    point.month = 3
    point.scheduled_date = timezone.localdate() + timedelta(days=1)
    point.organization = org
    point.batch.batch_number = "B-001"

    overdue = MagicMock()
    overdue.id = "point-2"
    overdue.month = 6
    overdue.scheduled_date = timezone.localdate() - timedelta(days=2)
    overdue.organization = org
    overdue.batch.batch_number = "B-002"

    pending_qs = MagicMock()
    pending_qs.select_related.return_value = [point]
    overdue_qs = MagicMock()
    overdue_qs.select_related.return_value = [overdue]

    memberships = list(org.memberships.select_related("user").filter(is_active=True))
    with patch("apps.schedule.models.TestPoint.objects.filter", side_effect=[pending_qs, overdue_qs]),          patch("apps.platform.models.Membership.objects.filter", return_value=MagicMock(select_related=MagicMock(return_value=memberships))),          patch("apps.notifications.tasks.Notification.objects.filter") as notification_filter,          patch("apps.notifications.tasks.create_notification") as create:
        notification_filter.return_value.exists.return_value = False
        result = notify_upcoming_and_overdue_test_points.run()
    assert result == 2 * len(memberships)
    assert create.call_count == result
