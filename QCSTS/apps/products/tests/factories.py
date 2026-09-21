import factory
from factory.django import DjangoModelFactory
from apps.products.models import Monograph, MonographTest, Product
from apps.accounts.tests.factories import UserFactory
from apps.platform.models import Membership, Organization, Role


def _default_org_for_user(user):
    if not user:
        return None
    membership = user.memberships.filter(is_active=True).order_by("created_at").first()
    if membership:
        return membership.organization
    org, _ = Organization.objects.get_or_create(
        slug="test-organization",
        defaults={"name": "Test Organization", "country": "EG"},
    )
    role, _ = Role.objects.get_or_create(organization=org, name=user.role or "analyst")
    Membership.objects.create(user=user, organization=org, role=role, default_site=None)
    return org


class MonographFactory(DjangoModelFactory):
    class Meta:
        model = Monograph

    name = factory.Sequence(lambda n: f"Monograph {n}")
    version = "1.0"
    effective_date = "2024-01-01"
    status = "draft"
    created_by = factory.SubFactory(UserFactory)
    organization = factory.LazyAttribute(lambda obj: _default_org_for_user(obj.created_by))


class ApprovedMonographFactory(MonographFactory):
    status = "approved"
    approved_by = factory.SubFactory(UserFactory)


class MonographTestFactory(DjangoModelFactory):
    class Meta:
        model = MonographTest

    monograph = factory.SubFactory(MonographFactory)
    name = factory.Sequence(lambda n: f"Test {n}")
    method = "USP <711>"
    specification = "98.0 - 102.0"
    unit = "%"
    sequence = factory.Sequence(lambda n: n)
    created_by = factory.SubFactory(UserFactory)
    # Derived from the monograph, not an independently-created default user's
    # org — a MonographTest must always share its monograph's organization,
    # and deriving it any other way is how this and the parent's `monograph`
    # SubFactory used to end up pointing at two different organizations.
    organization = factory.LazyAttribute(lambda obj: obj.monograph.organization)


class MonographWithTestsFactory(ApprovedMonographFactory):
    @classmethod
    def _after_postgeneration(cls, instance, create, results=None):
        if create and results:
            instance.save()

    @factory.post_generation
    def with_tests(obj, create, extracted, **kwargs):
        if not create:
            return
        MonographTestFactory(
            monograph=obj,
            name="Assay",
            method="HPLC",
            specification="98.0 - 102.0",
            unit="%",
            sequence=1,
        )


class ProductFactory(DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Sequence(lambda n: f"Product {n}")
    strength = "500 mg"
    dosage_form = "tablet"
    description = "Test product"
    created_by = factory.SubFactory(UserFactory)
    organization = factory.LazyAttribute(lambda obj: _default_org_for_user(obj.created_by))
    # Whatever organization this Product ends up with (default-derived above,
    # or an explicit override the caller passes) must also be the monograph's
    # organization — otherwise Product.monograph is a cross-tenant reference.
    # SelfAttribute("..organization") reads the parent's *resolved* value, so
    # this holds for both cases without the caller having to wire it by hand.
    monograph = factory.SubFactory(
        MonographWithTestsFactory,
        organization=factory.SelfAttribute("..organization"),
        created_by=factory.SelfAttribute("..created_by"),
    )
