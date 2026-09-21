import pytest
from django.db import IntegrityError, transaction

from apps.accounts.tests.factories import UserFactory
from apps.platform.models import Membership, Organization, Role


@pytest.mark.django_db
def test_user_can_have_only_one_active_tenant_membership():
    user = UserFactory()
    first = user.memberships.select_related("organization", "role").get()
    second_org = Organization.objects.create(name="Second", slug="second", country="EG")
    second_role = Role.objects.create(organization=second_org, name="analyst")

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Membership.objects.create(
                user=user,
                organization=second_org,
                role=second_role,
                is_active=True,
            )

    assert user.memberships.filter(is_active=True).count() == 1
