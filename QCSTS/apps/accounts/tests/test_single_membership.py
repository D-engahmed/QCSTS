import pytest
from rest_framework.test import APIClient

from apps.accounts.models import CustomUser


@pytest.mark.django_db
def test_registration_sets_password_changed_at():
    client = APIClient()
    response = client.post(
        "/api/v1/auth/register/",
        {
            "organization_name": "Password Audit Pharma",
            "slug": "password-audit-pharma",
            "country": "EG",
            "full_name": "Owner",
            "email": "password-owner@example.test",
            "password": "VerySecurePass123!",
        },
        format="json",
    )
    assert response.status_code == 201
    user = CustomUser.objects.get(email="password-owner@example.test")
    assert user.password_changed_at is not None
