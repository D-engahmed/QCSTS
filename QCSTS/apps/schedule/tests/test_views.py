import pytest
from rest_framework.test import APIClient
from apps.accounts.tests.factories import UserFactory
from apps.batches.tests.factories import BatchFactory
from apps.schedule.models import TestPoint
from datetime import date, timedelta


def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
class TestTestPointListView:

    def test_analyst_can_list_test_points(self):
        analyst = UserFactory()
        BatchFactory()
        c = auth_client(analyst)
        response = c.get("/api/v1/test-points/")
        assert response.status_code == 200
        assert response.data["success"] is True

    def test_unauthenticated_cannot_list_test_points(self):
        client = APIClient()
        response = client.get("/api/v1/test-points/")
        assert response.status_code == 401

    def test_filter_by_batch(self):
        analyst = UserFactory()
        batch = BatchFactory()
        c = auth_client(analyst)
        response = c.get(f"/api/v1/test-points/?batch={batch.id}")
        assert response.status_code == 200
        for tp in response.data["data"]:
            assert str(tp["batch"]) == str(batch.id)

    def test_filter_by_status(self):
        analyst = UserFactory()
        batch = BatchFactory()
        # mark one as overdue
        tp = TestPoint.objects.filter(batch=batch).first()
        tp.status = "overdue"
        tp.save()
        c = auth_client(analyst)
        response = c.get("/api/v1/test-points/?status=overdue")
        assert response.status_code == 200
        assert all(tp["status"] == "overdue" for tp in response.data["data"])

    def test_filter_upcoming(self):
        analyst = UserFactory()
        batch = BatchFactory()
        c = auth_client(analyst)
        response = c.get("/api/v1/test-points/?upcoming=true")
        assert response.status_code == 200


@pytest.mark.django_db
class TestTestPointDetailView:

    def test_analyst_can_get_test_point(self):
        analyst = UserFactory()
        batch = BatchFactory()
        tp = TestPoint.objects.filter(batch=batch).first()
        c = auth_client(analyst)
        response = c.get(f"/api/v1/test-points/{tp.id}/")
        assert response.status_code == 200
        assert str(tp.id) == response.data["data"]["id"]

    def test_nonexistent_test_point_returns_404(self):
        import uuid

        analyst = UserFactory()
        c = auth_client(analyst)
        response = c.get(f"/api/v1/test-points/{uuid.uuid4()}/")
        assert response.status_code == 404
