import factory
from factory.django import DjangoModelFactory
from apps.accounts.models import CustomUser
from apps.platform.models import Membership, Organization, Role, Site


def _ensure_default_organization_membership(user):
    if Membership.objects.filter(user=user).exists():
        return

    org, _ = Organization.objects.get_or_create(
        slug="test-organization",
        defaults={"name": "Test Organization", "country": "EG"},
    )
    site, _ = Site.objects.get_or_create(
        organization=org,
        name="Test Site",
        defaults={"country": "EG"},
    )
    role, _ = Role.objects.get_or_create(
        organization=org,
        name="analyst",
        defaults={"scope": "SITE"},
    )
    Membership.objects.create(
        user=user,
        organization=org,
        site=site,
        role=role,
    )


class UserFactory(DjangoModelFactory):
    class Meta:
        model = CustomUser

    email = factory.Sequence(lambda n: f"user{n}@cqsts.com")
    full_name = factory.Faker("name")
    is_active = True
    password = factory.PostGenerationMethodCall("set_password", "TestPass123!")

    @factory.post_generation
    def attach_default_membership(obj, create, extracted, **kwargs):
        if not create:
            return
        _ensure_default_organization_membership(obj)


class AdminFactory(UserFactory):
    is_staff = True


class QAManagerFactory(UserFactory):
    @factory.post_generation
    def set_role(obj, create, extracted, **kwargs):
        if create:
            obj.membership.role = Role.objects.get_or_create(
                organization=obj.membership.organization,
                name="qa_manager",
                defaults={"scope": "SITE"},
            )[0]
            obj.membership.role.save()


class SupervisorFactory(UserFactory):
    @factory.post_generation
    def set_role(obj, create, extracted, **kwargs):
        if create:
            obj.membership.role = Role.objects.get_or_create(
                organization=obj.membership.organization,
                name="supervisor",
                defaults={"scope": "SITE"},
            )[0]
            obj.membership.role.save()
