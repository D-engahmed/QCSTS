import factory
from factory.django import DjangoModelFactory
from apps.products.models import Monograph, MonographTest, Product
from apps.accounts.tests.factories import UserFactory


class MonographFactory(DjangoModelFactory):
    class Meta:
        model = Monograph

    name = factory.Sequence(lambda n: f"Monograph {n}")
    version = "1.0"
    effective_date = "2024-01-01"
    status = "draft"
    created_by = factory.SubFactory(UserFactory)


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


class MonographWithTestsFactory(ApprovedMonographFactory):
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
    monograph = factory.SubFactory(MonographWithTestsFactory)
    created_by = factory.SubFactory(UserFactory)
