import pytest
from django.core.exceptions import ValidationError

from apps.accounts.models import CustomUser
from apps.accounts.tests.factories import UserFactory
from apps.notifications.models import Notification
from apps.platform.models import Organization


@pytest.mark.django_db
def test_notification_must_share_tenant_with_user():
    org_b = Organization.objects.create(name="B Pharma", slug="b-pharma-notif", country="EG")
    user = UserFactory()
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
    user = UserFactory()
    org = user.memberships.select_related("organization").get().organization
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
