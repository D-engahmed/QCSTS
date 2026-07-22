import pytest
from rest_framework.test import APIClient
from apps.accounts.tests.factories import UserFactory, QAManagerFactory
from apps.batches.tests.factories import BatchFactory
from apps.schedule.models import TestPoint


def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
class TestDashboardView:

    def test_analyst_can_access_dashboard(self):
        analyst = UserFactory()
        c = auth_client(analyst)
        response = c.get("/api/v1/reports/dashboard/")
        assert response.status_code == 200
        assert response.data["success"] is True

    def test_dashboard_returns_summary(self):
        analyst = UserFactory()
        BatchFactory.create_batch(2)
        c = auth_client(analyst)
        response = c.get("/api/v1/reports/dashboard/")
        assert response.status_code == 200
        data = response.data["data"]
        assert "summary" in data
        assert "overdue_test_points" in data
        assert "upcoming_test_points" in data
        assert "failed_batches" in data
        assert "active_batches" in data

    def test_summary_counts_are_correct(self):
        analyst = UserFactory()
        BatchFactory.create_batch(3)
        c = auth_client(analyst)
        response = c.get("/api/v1/reports/dashboard/")
        summary = response.data["data"]["summary"]
        assert summary["active_batches"] == 3
        assert summary["total_products"] >= 3
        assert "overdue_tests" in summary
        assert "upcoming_tests" in summary

    def test_overdue_tests_appear_in_dashboard(self):
        analyst = UserFactory()
        batch = BatchFactory()
        tp = TestPoint.objects.filter(batch=batch).first()
        from datetime import date, timedelta

        tp.scheduled_date = date.today() - timedelta(days=5)
        tp.status = "overdue"
        tp.save()
        c = auth_client(analyst)
        response = c.get("/api/v1/reports/dashboard/")
        assert response.status_code == 200
        overdue = response.data["data"]["overdue_test_points"]
        assert len(overdue) >= 1
        assert overdue[0]["status"] == "overdue"

    def test_unauthenticated_cannot_access_dashboard(self):
        client = APIClient()
        response = client.get("/api/v1/reports/dashboard/")
        assert response.status_code == 401

    def test_qa_manager_can_access_dashboard(self):
        qa = QAManagerFactory()
        c = auth_client(qa)
        response = c.get("/api/v1/reports/dashboard/")
        assert response.status_code == 200
