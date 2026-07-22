import factory
from factory.django import DjangoModelFactory
from apps.results.models import TestResult
from apps.accounts.tests.factories import UserFactory
from apps.batches.tests.factories import BatchFactory
from apps.products.tests.factories import MonographTestFactory
from apps.schedule.models import TestPoint


class TestResultFactory(DjangoModelFactory):
    class Meta:
        model = TestResult

    test_point = factory.LazyAttribute(lambda o: TestPoint.objects.filter(batch=o.batch).first())
    monograph_test = factory.LazyAttribute(
        lambda o: o.test_point.batch.product.monograph.tests.first()
    )
    value = "99.5"
    unit = "%"
    specification_snapshot = "98.0 - 102.0"
    pass_fail = "pass"
    analyst = factory.SubFactory(UserFactory)
    notes = ""
    created_by = factory.SubFactory(UserFactory)

    class Params:
        batch = factory.SubFactory(BatchFactory)
