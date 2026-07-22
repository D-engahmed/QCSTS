import pytest
from rest_framework.test import APIClient
from apps.products.tests.factories import (
    MonographFactory,
    ApprovedMonographFactory,
    MonographTestFactory,
    ProductFactory,
)
from apps.accounts.tests.factories import (
    UserFactory,
    AdminFactory,
    QAManagerFactory,
)


def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
class TestMonographViews:

    def test_analyst_can_list_monographs(self):
        analyst = UserFactory()
        MonographFactory.create_batch(3)
        c = auth_client(analyst)
        response = c.get("/api/v1/products/monographs/")
        assert response.status_code == 200
        assert len(response.data["data"]) == 3

    def test_analyst_can_create_monograph(self):
        analyst = UserFactory()
        c = auth_client(analyst)
        response = c.post(
            "/api/v1/products/monographs/",
            {
                "name": "BP Monograph",
                "version": "1.0",
                "effective_date": "2024-01-01",
                "status": "draft",
            },
        )
        assert response.status_code == 201
        assert response.data["data"]["name"] == "BP Monograph"

    def test_unauthenticated_cannot_list_monographs(self):
        client = APIClient()
        response = client.get("/api/v1/products/monographs/")
        assert response.status_code == 401

    def test_analyst_can_get_monograph_detail(self):
        analyst = UserFactory()
        monograph = MonographFactory()
        c = auth_client(analyst)
        response = c.get(f"/api/v1/products/monographs/{monograph.id}/")
        assert response.status_code == 200
        assert str(monograph.id) == response.data["data"]["id"]

    def test_analyst_can_update_draft_monograph(self):
        analyst = UserFactory()
        monograph = MonographFactory()
        c = auth_client(analyst)
        response = c.patch(f"/api/v1/products/monographs/{monograph.id}/", {"version": "2.0"})
        assert response.status_code == 200

    def test_cannot_update_approved_monograph(self):
        analyst = UserFactory()
        monograph = ApprovedMonographFactory()
        c = auth_client(analyst)
        response = c.patch(f"/api/v1/products/monographs/{monograph.id}/", {"version": "2.0"})
        assert response.status_code == 409

    def test_qa_manager_can_approve_monograph(self):
        qa = QAManagerFactory()
        monograph = MonographFactory()
        c = auth_client(qa)
        response = c.post(f"/api/v1/products/monographs/{monograph.id}/approve/")
        assert response.status_code == 200
        assert response.data["data"]["status"] == "approved"

    def test_analyst_cannot_approve_monograph(self):
        analyst = UserFactory()
        monograph = MonographFactory()
        c = auth_client(analyst)
        response = c.post(f"/api/v1/products/monographs/{monograph.id}/approve/")
        assert response.status_code == 403

    def test_cannot_approve_already_approved_monograph(self):
        qa = QAManagerFactory()
        monograph = ApprovedMonographFactory()
        c = auth_client(qa)
        response = c.post(f"/api/v1/products/monographs/{monograph.id}/approve/")
        assert response.status_code == 409


@pytest.mark.django_db
class TestMonographTestViews:

    def test_analyst_can_add_test_to_draft_monograph(self):
        analyst = UserFactory()
        monograph = MonographFactory()
        c = auth_client(analyst)
        response = c.post(
            f"/api/v1/products/monographs/{monograph.id}/tests/",
            {
                "name": "Assay",
                "method": "HPLC",
                "specification": "98.0% - 102.0%",
                "unit": "%",
                "sequence": 1,
            },
        )
        assert response.status_code == 201
        assert response.data["data"]["name"] == "Assay"

    def test_cannot_add_test_to_approved_monograph(self):
        analyst = UserFactory()
        monograph = ApprovedMonographFactory()
        c = auth_client(analyst)
        response = c.post(
            f"/api/v1/products/monographs/{monograph.id}/tests/",
            {
                "name": "Assay",
                "method": "HPLC",
                "specification": "98.0% - 102.0%",
                "unit": "%",
                "sequence": 1,
            },
        )
        assert response.status_code == 409

    def test_analyst_can_list_monograph_tests(self):
        analyst = UserFactory()
        monograph = MonographFactory()
        MonographTestFactory.create_batch(3, monograph=monograph)
        c = auth_client(analyst)
        response = c.get(f"/api/v1/products/monographs/{monograph.id}/tests/")
        assert response.status_code == 200
        assert len(response.data["data"]) == 3


@pytest.mark.django_db
class TestProductViews:

    def test_analyst_can_list_products(self):
        analyst = UserFactory()
        ProductFactory.create_batch(3)
        c = auth_client(analyst)
        response = c.get("/api/v1/products/")
        assert response.status_code == 200
        assert len(response.data["data"]) == 3

    def test_analyst_can_create_product(self):
        analyst = UserFactory()
        monograph = ApprovedMonographFactory()
        c = auth_client(analyst)
        response = c.post(
            "/api/v1/products/",
            {
                "name": "Amoxicillin",
                "strength": "500 mg",
                "dosage_form": "capsule",
                "monograph": str(monograph.id),
            },
        )
        assert response.status_code == 201
        assert response.data["data"]["name"] == "Amoxicillin"

    def test_analyst_can_get_product_detail(self):
        analyst = UserFactory()
        product = ProductFactory()
        c = auth_client(analyst)
        response = c.get(f"/api/v1/products/{product.id}/")
        assert response.status_code == 200

    def test_analyst_can_update_product(self):
        analyst = UserFactory()
        product = ProductFactory()
        c = auth_client(analyst)
        response = c.patch(
            f"/api/v1/products/{product.id}/", {"description": "Updated description"}
        )
        assert response.status_code == 200

    def test_unauthenticated_cannot_access_products(self):
        client = APIClient()
        response = client.get("/api/v1/products/")
        assert response.status_code == 401
