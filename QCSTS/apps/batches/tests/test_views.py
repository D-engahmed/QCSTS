import pytest
from rest_framework.test import APIClient
from apps.accounts.tests.factories import UserFactory, AdminFactory
from apps.batches.tests.factories import BatchFactory
from apps.products.tests.factories import ProductFactory, ApprovedMonographFactory
from apps.schedule.models import TestPoint


def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
class TestBatchListCreateView:

    def test_analyst_can_list_batches(self):
        analyst = UserFactory()
        BatchFactory.create_batch(3)
        c = auth_client(analyst)
        response = c.get("/api/v1/batches/")
        assert response.status_code == 200
        assert len(response.data["data"]) == 3

    def test_analyst_can_create_batch(self):
        analyst = UserFactory()
        product = ProductFactory()
        from datetime import date

        c = auth_client(analyst)
        response = c.post(
            "/api/v1/batches/",
            {
                "product": str(product.id),
                "batch_number": "TEST-2024-001",
                "mfg_date": str(date.today()),
                "expiry_date": "2027-01-01",
                "incubation_date": str(date.today()),
                "study_type": "accelerated",
                "shelf": "S99",
                "rack": "R99",
                "position": "P99",
                "qty_placed": 30,
            },
        )
        assert response.status_code == 201
        assert response.data["data"]["batch_number"] == "TEST-2024-001"

    def test_creating_batch_generates_test_points(self):
        analyst = UserFactory()
        product = ProductFactory()
        from datetime import date

        c = auth_client(analyst)
        response = c.post(
            "/api/v1/batches/",
            {
                "product": str(product.id),
                "batch_number": "TEST-2024-002",
                "mfg_date": str(date.today()),
                "expiry_date": "2027-01-01",
                "incubation_date": str(date.today()),
                "study_type": "accelerated",
                "shelf": "S98",
                "rack": "R98",
                "position": "P98",
                "qty_placed": 30,
            },
        )
        assert response.status_code == 201
        batch_id = response.data["data"]["id"]
        from apps.batches.models import Batch

        batch = Batch.objects.get(id=batch_id)
        assert TestPoint.objects.filter(batch=batch).count() == 3

    def test_duplicate_batch_number_rejected(self):
        analyst = UserFactory()
        batch = BatchFactory(batch_number="DUP-2024-001")
        from datetime import date

        c = auth_client(analyst)
        response = c.post(
            "/api/v1/batches/",
            {
                "product": str(batch.product.id),
                "batch_number": "DUP-2024-001",
                "mfg_date": str(date.today()),
                "expiry_date": "2027-01-01",
                "incubation_date": str(date.today()),
                "study_type": "accelerated",
                "shelf": "S97",
                "rack": "R97",
                "position": "P97",
                "qty_placed": 30,
            },
        )
        assert response.status_code in [400, 409]

    def test_incubation_before_mfg_date_rejected(self):
        analyst = UserFactory()
        product = ProductFactory()
        c = auth_client(analyst)
        response = c.post(
            "/api/v1/batches/",
            {
                "product": str(product.id),
                "batch_number": "TEST-2024-003",
                "mfg_date": "2024-06-01",
                "expiry_date": "2027-01-01",
                "incubation_date": "2024-01-01",
                "study_type": "accelerated",
                "shelf": "S96",
                "rack": "R96",
                "position": "P96",
                "qty_placed": 30,
            },
        )
        assert response.status_code == 400

    def test_unauthenticated_cannot_create_batch(self):
        client = APIClient()
        response = client.post("/api/v1/batches/", {})
        assert response.status_code == 401


@pytest.mark.django_db
class TestBatchDetailView:

    def test_analyst_can_get_batch(self):
        analyst = UserFactory()
        batch = BatchFactory()
        c = auth_client(analyst)
        response = c.get(f"/api/v1/batches/{batch.id}/")
        assert response.status_code == 200
        assert response.data["data"]["batch_number"] == batch.batch_number

    def test_batch_detail_includes_test_points(self):
        analyst = UserFactory()
        batch = BatchFactory(study_type="accelerated")
        c = auth_client(analyst)
        response = c.get(f"/api/v1/batches/{batch.id}/")
        assert response.status_code == 200
        assert len(response.data["data"]["test_points"]) == 3

    def test_nonexistent_batch_returns_404(self):
        import uuid

        analyst = UserFactory()
        c = auth_client(analyst)
        response = c.get(f"/api/v1/batches/{uuid.uuid4()}/")
        assert response.status_code == 404
