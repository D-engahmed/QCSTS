import factory
from factory.django import DjangoModelFactory
from datetime import date
from apps.schedule.models import TestPoint
from apps.accounts.tests.factories import UserFactory


class TestPointFactory(DjangoModelFactory):
    class Meta:
        model = TestPoint

    batch = None
    month = factory.Sequence(lambda n: n * 3)
    scheduled_date = factory.LazyFunction(date.today)
    status = "pending"
    created_by = factory.SubFactory(UserFactory)
