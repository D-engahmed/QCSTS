import pytest
from rest_framework.test import APIClient

from apps.accounts.tests.factories import AdminFactory, UserFactory
from apps.quality.models import Deviation


@pytest.mark.django_db
def test_quality_event_cannot_change_lifecycle_status_through_patch():
    user = AdminFactory()
    org = user.memberships.select_related("organization").get().organization
    event = Deviation.objects.create(
        organization=org,
        created_by=user,
        owner=user,
        reference="DEV-001",
        title="Temperature excursion",
        description="Chamber temperature exceeded limit.",
    )
    client = APIClient()
    client.force_authenticate(user=user)
    client.credentials(HTTP_X_ORGANIZATION_ID=str(org.id))

    response = client.patch(
        f"/api/v1/quality/deviations/{event.id}/",
        {"status": "approved"},
        format="json",
    )

    assert response.status_code == 200
    event.refresh_from_db()
    assert event.status == "open"


@pytest.mark.django_db
def test_quality_transition_requires_comments():
    user = AdminFactory()
    org = user.memberships.select_related("organization").get().organization
    event = Deviation.objects.create(
        organization=org,
        created_by=user,
        owner=user,
        reference="DEV-002",
        title="Temperature excursion",
        description="Chamber temperature exceeded limit.",
    )
    client = APIClient()
    client.force_authenticate(user=user)
    client.credentials(HTTP_X_ORGANIZATION_ID=str(org.id))

    response = client.post(
        f"/api/v1/quality/deviations/{event.id}/transition/",
        {"status": "investigation"},
        format="json",
    )

    assert response.status_code == 400
