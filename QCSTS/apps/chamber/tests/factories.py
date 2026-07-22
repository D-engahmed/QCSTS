import factory
from factory.django import DjangoModelFactory
from apps.chamber.models import SamplePull, LocationHistory
from apps.accounts.tests.factories import UserFactory
from apps.batches.tests.factories import BatchFactory


class SamplePullFactory(DjangoModelFactory):
    class Meta:
        model = SamplePull

    batch = factory.SubFactory(BatchFactory)
    qty_pulled = 5
    pulled_by = factory.SubFactory(UserFactory)
    notes = ""
    created_by = factory.SubFactory(UserFactory)


class LocationHistoryFactory(DjangoModelFactory):
    class Meta:
        model = LocationHistory

    batch = factory.SubFactory(BatchFactory)
    old_shelf = "S1"
    old_rack = "R1"
    old_position = "P1"
    new_shelf = "S2"
    new_rack = "R2"
    new_position = "P2"
    changed_by = factory.SubFactory(UserFactory)
    created_by = factory.SubFactory(UserFactory)
