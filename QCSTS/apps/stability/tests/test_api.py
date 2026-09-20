import pytest
from rest_framework.test import APIClient

from apps.accounts.models import CustomUser
from apps.accounts.tests.factories import UserFactory
from apps.platform.models import Membership, Organization, Role
from apps.stability.models import StorageCondition


@pytest.mark.django_db
def test_stability_storage_conditions_are_tenant_scoped():
    user = UserFactory()
    first_membership = user.memberships.select_related("organization", "role").get()
    first_org = first_membership.organization

    second_org = Organization.objects.create(
        name="Second Pharma",
        slug="second-pharma",
        country="EG",
    )
    second_role = Role.objects.create(
        organization=second_org,
        name="analyst",
    )
    second_user = CustomUser.objects.create_user(
        email="second@example.test",
        password="TestPass123!",
        full_name="Second User",
    )
    Membership.objects.create(
        user=second_user,
        organization=second_org,
        role=second_role,
    )

    first_condition = StorageCondition.objects.create(
        organization=first_org,
        code="25C",
        name="25°C / 60% RH",
    )
    second_condition = StorageCondition.objects.create(
        organization=second_org,
        code="30C",
        name="30°C / 75% RH",
    )

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get("/api/v1/stability/storage-conditions/")

    assert response.status_code == 200
    ids = {item["id"] for item in response.data["results"]} if isinstance(response.data.get("results"), list) else {
        item["id"] for item in response.data["data"]
    }
    assert str(first_condition.id) in ids
    assert str(second_condition.id) not in ids
