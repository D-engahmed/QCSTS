import pytest
from django.core.exceptions import ValidationError

from apps.accounts.models import CustomUser
from apps.notifications.models import Notification
from apps.platform.models import Organization


@pytest.mark.django_db
def test_notification_must_share_tenant_with_user():
    org_b = Organization.objects.create(name="B Pharma", slug="b-pharma-notif", country="EG")
    user = CustomUser.objects.create_user(
        email="notif-user@a.test",
        password="Strong-password-123",
        full_name="Notification User",
        role="analyst",
    )
    record = Notification(
        organization=org_b,
        user=user,
        title="Cross tenant",
        body="Should be rejected",
    )
    with pytest.raises(ValidationError):
        record.save()


@pytest.mark.django_db
def test_notification_can_be_created_for_same_tenant_user():
    org = Organization.objects.create(name="Tenant Pharma", slug="tenant-notif", country="EG")
    user = CustomUser.objects.create_user(
        email="notif-user@tenant.test",
        password="Strong-password-123",
        full_name="Notification User",
        role="analyst",
    )
    record = Notification.objects.create(
        organization=org,
        user=user,
        title="Operational alert",
        body="Test point due",
        kind=Notification.Kind.OVERDUE,
        severity=Notification.Severity.WARNING,
    )
    assert record.organization_id == org.id
    assert record.user_id == user.id
