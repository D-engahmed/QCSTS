import pytest
from rest_framework.test import APIClient

from apps.accounts.tests.factories import AdminFactory
from apps.platform.models import Organization, Role, Site


@pytest.mark.django_db
def test_staff_creation_cannot_assign_a_foreign_organization_site():
    admin = AdminFactory()
    foreign_org = Organization.objects.create(
        name="Foreign Organization", slug="foreign-organization", country="EG"
    )
    foreign_site = Site.objects.create(
        organization=foreign_org, name="Foreign Site", country="EG"
    )

    client = APIClient()
    client.force_authenticate(user=admin)

    response = client.post(
        "/api/v1/auth/users/",
        {
            "email": "foreign-site@example.com",
            "full_name": "Foreign Site User",
            "role": "analyst",
            "site_id": str(foreign_site.id),
            "password": "SafePassword123!",
        },
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_customer_user_response_exposes_one_authorization_context():
    admin = AdminFactory()
    client = APIClient()
    client.force_authenticate(user=admin)

    response = client.get("/api/v1/auth/me/")

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["organization"]["id"] == str(admin.membership.organization_id)
    assert payload["site"]["id"] == str(admin.membership.site_id)
    assert payload["role"] == admin.membership.role.name
    assert payload["role_scope"] == admin.membership.role.scope
