import pytest
from rest_framework.test import APIClient
from apps.audit.tests.factories import AuditLogFactory
from apps.accounts.tests.factories import UserFactory, AdminFactory, QAManagerFactory


@pytest.fixture
def client():
    return APIClient()


def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
class TestAuditLogListView:

    def test_qa_manager_can_view_audit_trail(self):
        qa = QAManagerFactory()
        AuditLogFactory.create_batch(3)
        c = auth_client(qa)
        response = c.get("/api/v1/audit/")
        assert response.status_code == 200
        assert response.data["success"] is True
        assert len(response.data["data"]) == 3

    def test_admin_can_view_audit_trail(self):
        admin = AdminFactory()
        AuditLogFactory()
        c = auth_client(admin)
        response = c.get("/api/v1/audit/")
        assert response.status_code == 200

    def test_analyst_cannot_view_audit_trail(self):
        analyst = UserFactory()
        c = auth_client(analyst)
        response = c.get("/api/v1/audit/")
        assert response.status_code == 403

    def test_unauthenticated_cannot_view_audit_trail(self, client):
        response = client.get("/api/v1/audit/")
        assert response.status_code == 401

    def test_filter_by_model_name(self):
        qa = QAManagerFactory()
        AuditLogFactory(model_name="Batch")
        AuditLogFactory(model_name="Product")
        c = auth_client(qa)
        response = c.get("/api/v1/audit/?model_name=Batch")
        assert response.status_code == 200
        assert all(log["model_name"] == "Batch" for log in response.data["data"])

    def test_filter_by_action(self):
        qa = QAManagerFactory()
        AuditLogFactory(action="CREATE")
        AuditLogFactory(action="UPDATE")
        c = auth_client(qa)
        response = c.get("/api/v1/audit/?action=CREATE")
        assert response.status_code == 200
        assert all(log["action"] == "CREATE" for log in response.data["data"])


@pytest.mark.django_db
class TestAuditLogDetailView:

    def test_qa_manager_can_view_single_log(self):
        qa = QAManagerFactory()
        log = AuditLogFactory()
        c = auth_client(qa)
        response = c.get(f"/api/v1/audit/{log.id}/")
        assert response.status_code == 200
        assert str(log.id) == response.data["data"]["id"]

    def test_nonexistent_log_returns_404(self):
        import uuid

        qa = QAManagerFactory()
        c = auth_client(qa)
        response = c.get(f"/api/v1/audit/{uuid.uuid4()}/")
        assert response.status_code == 404
