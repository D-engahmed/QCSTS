import pytest
from rest_framework.test import APIClient
from apps.accounts.tests.factories import UserFactory
from apps.batches.tests.factories import BatchFactory
from apps.chamber.tests.factories import SamplePullFactory


def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
class TestChamberInventoryView:

    def test_analyst_can_view_chamber(self):
        analyst = UserFactory()
        BatchFactory.create_batch(3)
        c = auth_client(analyst)
        response = c.get("/api/v1/chamber/")
        assert response.status_code == 200
        assert response.data["success"] is True

    def test_unauthenticated_cannot_view_chamber(self):
        client = APIClient()
        response = client.get("/api/v1/chamber/")
        assert response.status_code == 401

    def test_filter_by_study_type(self):
        analyst = UserFactory()
        BatchFactory(study_type="long_term")
        BatchFactory(study_type="accelerated")
        c = auth_client(analyst)
        response = c.get("/api/v1/chamber/?study_type=long_term")
        assert response.status_code == 200
        assert all(b["study_type"] == "long_term" for b in response.data["data"])


@pytest.mark.django_db
class TestSamplePullView:

    def test_analyst_can_record_pull(self):
        analyst = UserFactory()
        batch = BatchFactory(qty_placed=60, qty_remaining=60)
        c = auth_client(analyst)
        response = c.post(
            "/api/v1/chamber/pulls/",
            {
                "batch": str(batch.id),
                "qty_pulled": 5,
            },
        )
        assert response.status_code == 201
        batch.refresh_from_db()
        assert batch.qty_remaining == 55

    def test_cannot_pull_more_than_remaining(self):
        analyst = UserFactory()
        batch = BatchFactory(qty_placed=10, qty_remaining=10)
        c = auth_client(analyst)
        response = c.post(
            "/api/v1/chamber/pulls/",
            {
                "batch": str(batch.id),
                "qty_pulled": 99,
            },
        )
        assert response.status_code == 422

    def test_analyst_can_list_pulls(self):
        analyst = UserFactory()
        batch = BatchFactory()
        c = auth_client(analyst)
        response = c.get("/api/v1/chamber/pulls/")
        assert response.status_code == 200

    def test_filter_pulls_by_batch(self):
        analyst = UserFactory()
        batch = BatchFactory()
        c = auth_client(analyst)
        response = c.get(f"/api/v1/chamber/pulls/?batch={batch.id}")
        assert response.status_code == 200


@pytest.mark.django_db
class TestChangeBatchLocationView:

    def test_analyst_can_move_batch(self):
        analyst = UserFactory()
        batch = BatchFactory(shelf="S1", rack="R1", position="P1")
        c = auth_client(analyst)
        response = c.post(
            "/api/v1/chamber/move/",
            {
                "batch": str(batch.id),
                "new_shelf": "S9",
                "new_rack": "R9",
                "new_position": "P9",
                "reason": "Reorganization",
            },
        )
        assert response.status_code == 201
        batch.refresh_from_db()
        assert batch.shelf == "S9"
        assert batch.rack == "R9"
        assert batch.position == "P9"

    def test_cannot_move_to_occupied_location(self):
        analyst = UserFactory()
        batch1 = BatchFactory(shelf="S1", rack="R1", position="P1")
        batch2 = BatchFactory(shelf="S2", rack="R2", position="P2")
        c = auth_client(analyst)
        response = c.post(
            "/api/v1/chamber/move/",
            {
                "batch": str(batch2.id),
                "new_shelf": "S1",
                "new_rack": "R1",
                "new_position": "P1",
            },
        )
        assert response.status_code == 400

    def test_unauthenticated_cannot_move_batch(self):
        client = APIClient()
        response = client.post("/api/v1/chamber/move/", {})
        assert response.status_code == 401


@pytest.mark.django_db
class TestLocationHistoryView:

    def test_analyst_can_view_location_history(self):
        analyst = UserFactory()
        batch = BatchFactory()
        c = auth_client(analyst)
        response = c.get(f"/api/v1/chamber/locations/{batch.id}/")
        assert response.status_code == 200
        assert response.data["success"] is True
