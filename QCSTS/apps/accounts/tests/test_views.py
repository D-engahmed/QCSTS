import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from apps.accounts.tests.factories import UserFactory, AdminFactory


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def analyst(db):
    return UserFactory()


@pytest.fixture
def admin(db):
    return AdminFactory()


def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
class TestLoginView:

    def test_login_success(self, client, analyst):
        response = client.post(
            "/api/v1/auth/login/", {"email": analyst.email, "password": "TestPass123!"}
        )
        assert response.status_code == 200
        assert response.data["success"] is True
        assert "access" in response.data["data"]
        assert "refresh" in response.data["data"]
        assert response.data["data"]["user"]["email"] == analyst.email

    def test_login_wrong_password(self, client, analyst):
        response = client.post(
            "/api/v1/auth/login/", {"email": analyst.email, "password": "WrongPassword!"}
        )
        assert response.status_code == 401
        assert response.data["success"] is False

    def test_login_nonexistent_user(self, client):
        response = client.post(
            "/api/v1/auth/login/", {"email": "nobody@cqsts.com", "password": "TestPass123!"}
        )
        assert response.status_code == 400
        assert response.data["success"] is False

    def test_login_locked_account(self, client, analyst):
        analyst.is_active = False
        analyst.save()
        response = client.post(
            "/api/v1/auth/login/", {"email": analyst.email, "password": "TestPass123!"}
        )
        assert response.status_code == 403
        assert response.data["success"] is False


@pytest.mark.django_db
class TestMeView:

    def test_me_returns_current_user(self, analyst):
        c = auth_client(analyst)
        response = c.get("/api/v1/auth/me/")
        assert response.status_code == 200
        assert response.data["data"]["email"] == analyst.email

    def test_me_requires_authentication(self, client):
        response = client.get("/api/v1/auth/me/")
        assert response.status_code == 401


@pytest.mark.django_db
class TestUserManagement:

    def test_admin_can_create_user(self, admin):
        c = auth_client(admin)
        response = c.post(
            "/api/v1/auth/users/",
            {
                "email": "newuser@cqsts.com",
                "full_name": "New User",
                "role": "analyst",
                "password": "SecurePass123!",
            },
        )
        assert response.status_code == 201
        assert response.data["data"]["email"] == "newuser@cqsts.com"

    def test_analyst_cannot_create_user(self, analyst):
        c = auth_client(analyst)
        response = c.post(
            "/api/v1/auth/users/",
            {
                "email": "newuser@cqsts.com",
                "full_name": "New User",
                "role": "analyst",
                "password": "SecurePass123!",
            },
        )
        assert response.status_code == 403

    def test_admin_can_list_users(self, admin):
        c = auth_client(admin)
        response = c.get("/api/v1/auth/users/")
        assert response.status_code == 200
        assert response.data["success"] is True

    def test_analyst_cannot_list_users(self, analyst):
        c = auth_client(analyst)
        response = c.get("/api/v1/auth/users/")
        assert response.status_code == 403


@pytest.mark.django_db
class TestUserDetailView:

    def test_admin_can_get_user(self, admin):
        user = UserFactory()
        c = auth_client(admin)
        response = c.get(f"/api/v1/auth/users/{user.id}/")
        assert response.status_code == 200
        assert response.data["data"]["email"] == user.email

    def test_admin_can_deactivate_user(self, admin):
        user = UserFactory()
        c = auth_client(admin)
        response = c.delete(f"/api/v1/auth/users/{user.id}/")
        assert response.status_code == 200
        user.refresh_from_db()
        assert user.is_active is False

    def test_admin_can_update_user(self, admin):
        user = UserFactory()
        c = auth_client(admin)
        response = c.patch(f"/api/v1/auth/users/{user.id}/", {"full_name": "Updated Name"})
        assert response.status_code == 200

    def test_get_nonexistent_user_returns_404(self, admin):
        import uuid

        c = auth_client(admin)
        response = c.get(f"/api/v1/auth/users/{uuid.uuid4()}/")
        assert response.status_code == 404


@pytest.mark.django_db
class TestChangePasswordView:

    def test_user_can_change_password(self, analyst):
        c = auth_client(analyst)
        response = c.post(
            "/api/v1/auth/change-password/",
            {"current_password": "TestPass123!", "new_password": "NewSecurePass123!"},
        )
        assert response.status_code == 200

    def test_wrong_current_password_fails(self, analyst):
        c = auth_client(analyst)
        response = c.post(
            "/api/v1/auth/change-password/",
            {"current_password": "WrongPassword!", "new_password": "NewSecurePass123!"},
        )
        assert response.status_code == 400
