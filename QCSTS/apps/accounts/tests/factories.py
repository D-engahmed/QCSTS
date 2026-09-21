import factory
from factory.django import DjangoModelFactory
from apps.accounts.models import CustomUser
from apps.platform.models import Membership, Organization, Role


def _ensure_default_organization_membership(user):
    if Membership.objects.filter(user=user).exists():
        return

    org, _ = Organization.objects.get_or_create(
        slug="test-organization",
        defaults={"name": "Test Organization", "country": "EG"},
    )
    role, _ = Role.objects.get_or_create(
        organization=org,
        name=user.role or "analyst",
    )
    Membership.objects.create(
        user=user,
        organization=org,
        role=role,
        default_site=None,
    )


class UserFactory(DjangoModelFactory):
    class Meta:
        model = CustomUser

    email = factory.Sequence(lambda n: f"user{n}@cqsts.com")
    full_name = factory.Faker("name")
    role = "analyst"
    is_active = True
    password = factory.PostGenerationMethodCall("set_password", "TestPass123!")

    @classmethod
    def _after_postgeneration(cls, instance, create, results=None):
        # Preserve the final save without factory_boy's deprecated warning path.
        if create and results:
            instance.save()

    @factory.post_generation
    def attach_default_membership(obj, create, extracted, **kwargs):
        if not create:
            return
        _ensure_default_organization_membership(obj)


class AdminFactory(UserFactory):
    role = "admin"
    is_staff = True


class QAManagerFactory(UserFactory):
    role = "qa_manager"


class SupervisorFactory(UserFactory):
    role = "supervisor"
