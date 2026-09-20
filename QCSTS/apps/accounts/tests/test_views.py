import pytest
from rest_framework.test import APIClient

from apps.accounts.models import CustomUser
from apps.accounts.tests.factories import AdminFactory, UserFactory
from apps.platform.models import Organization


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

    def test_login_nonexistent_user_is_indistinguishable_from_wrong_password(self, client, analyst):
        unknown = client.post(
            "/api/v1/auth/login/",
            {"email": "nobody@cqsts.com", "password": "TestPass123!"},
        )
        wrong_pw = client.post(
            "/api/v1/auth/login/",
            {"email": analyst.email, "password": "WrongPassword!"},
        )
        assert unknown.status_code == wrong_pw.status_code == 401
        assert unknown.data == wrong_pw.data

    def test_login_locked_account_leaks_no_account_state(self, client, analyst):
        for _ in range(5):
            analyst.register_failed_login()
        response = client.post(
            "/api/v1/auth/login/", {"email": analyst.email, "password": "TestPass123!"}
        )
        assert response.status_code == 401
        assert response.data["success"] is False

    def test_deactivated_account_cannot_log_in(self, client, analyst):
        analyst.is_active = False
        analyst.save()
        response = client.post(
            "/api/v1/auth/login/", {"email": analyst.email, "password": "TestPass123!"}
        )
        assert response.status_code == 401


@pytest.mark.django_db
class TestMeView:
    def test_me_returns_current_user(self, analyst):
        response = auth_client(analyst).get("/api/v1/auth/me/")
        assert response.status_code == 200
        assert response.data["data"]["email"] == analyst.email

    def test_me_requires_authentication(self, client):
        response = client.get("/api/v1/auth/me/")
        assert response.status_code == 401


@pytest.mark.django_db
class TestUserManagement:
    def test_admin_can_create_user(self, admin):
        response = auth_client(admin).post(
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
        response = auth_client(analyst).post(
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
        response = auth_client(admin).get("/api/v1/auth/users/")
        assert response.status_code == 200
        assert response.data["success"] is True

    def test_analyst_cannot_list_users(self, analyst):
        response = auth_client(analyst).get("/api/v1/auth/users/")
        assert response.status_code == 403


@pytest.mark.django_db
class TestUserDetailView:
    def test_admin_can_get_user(self, admin):
        user = UserFactory()
        response = auth_client(admin).get(f"/api/v1/auth/users/{user.id}/")
        assert response.status_code == 200
        assert response.data["data"]["email"] == user.email

    def test_admin_revokes_org_membership_not_the_global_account(self, admin):
        user = UserFactory()
        response = auth_client(admin).delete(f"/api/v1/auth/users/{user.id}/")
        assert response.status_code == 200
        user.refresh_from_db()
        assert user.is_active is True
        assert user.memberships.filter(is_active=True).exists() is False

    def test_admin_cannot_revoke_their_own_membership(self, admin):
        response = auth_client(admin).delete(f"/api/v1/auth/users/{admin.id}/")
        assert response.status_code == 400

    def test_admin_can_update_user(self, admin):
        user = UserFactory()
        response = auth_client(admin).patch(
            f"/api/v1/auth/users/{user.id}/", {"full_name": "Updated Name"}
        )
        assert response.status_code == 200

    def test_get_nonexistent_user_returns_404(self, admin):
        import uuid

        response = auth_client(admin).get(f"/api/v1/auth/users/{uuid.uuid4()}/")
        assert response.status_code == 404


@pytest.mark.django_db
class TestChangePasswordView:
    def test_user_can_change_password(self, analyst):
        response = auth_client(analyst).post(
            "/api/v1/auth/change-password/",
            {
                "current_password": "TestPass123!",
                "new_password": "NewSecurePass123!",
            },
        )
        assert response.status_code == 200

    def test_wrong_current_password_fails(self, analyst):
        response = auth_client(analyst).post(
            "/api/v1/auth/change-password/",
            {
                "current_password": "WrongPassword!",
                "new_password": "NewSecurePass123!",
            },
        )
        assert response.status_code == 400


@pytest.mark.django_db
class TestOrganizationRegistration:
    def test_register_creates_tenant_owner_and_returns_tokens(self, client):
        response = client.post(
            "/api/v1/auth/register/",
            {
                "organization_name": "Acme Pharma",
                "legal_name": "Acme Pharma Ltd.",
                "slug": "acme-pharma",
                "country": "eg",
                "timezone": "Africa/Cairo",
                "currency": "EGP",
                "site_name": "Cairo QC Lab",
                "site_address": "Cairo, Egypt",
                "full_name": "Lab Administrator",
                "email": "owner@acme-pharma.example",
                "password": "VerySecurePass123!",
            },
            format="json",
        )
        assert response.status_code == 201
        assert response.data["success"] is True
        assert response.data["data"]["user"]["organization_role"] == "admin"
        assert response.data["data"]["organization"]["slug"] == "acme-pharma"
        assert response.data["data"]["site"]["name"] == "Cairo QC Lab"

        user = CustomUser.objects.get(email="owner@acme-pharma.example")
        membership = user.memberships.select_related("organization", "role").get()
        assert membership.organization.slug == "acme-pharma"
        assert membership.role.name == "admin"
        assert membership.is_active is True

    def test_register_rejects_duplicate_email(self, client):
        existing_user = UserFactory()
        response = client.post(
            "/api/v1/auth/register/",
            {
                "organization_name": "Another Pharma",
                "country": "EG",
                "full_name": "Another Owner",
                "email": existing_user.email,
                "password": "VerySecurePass123!",
            },
            format="json",
        )
        assert response.status_code == 400
        assert "email" in response.data["errors"]

    def test_register_rejects_duplicate_slug(self, client):
        Organization.objects.create(
            slug="test-organization", name="Test Org", country="EG"
        )
        response = client.post(
            "/api/v1/auth/register/",
            {
                "organization_name": "First Pharma",
                "slug": "test-organization",
                "country": "EG",
                "full_name": "Owner",
                "email": "new-owner@example.com",
                "password": "VerySecurePass123!",
            },
            format="json",
        )
        assert response.status_code == 400
        assert "slug" in response.data["errors"]
