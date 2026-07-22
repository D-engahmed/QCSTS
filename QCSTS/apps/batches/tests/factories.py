import factory
from factory.django import DjangoModelFactory
from datetime import date
from apps.batches.models import Batch
from apps.accounts.tests.factories import UserFactory
from apps.products.tests.factories import ProductFactory


class BatchFactory(DjangoModelFactory):
    class Meta:
        model = Batch

    product = factory.SubFactory(ProductFactory)
    batch_number = factory.Sequence(lambda n: f"BATCH-{n:04d}")
    mfg_date = factory.LazyFunction(date.today)
    expiry_date = factory.LazyFunction(lambda: date.today().replace(year=date.today().year + 3))
    incubation_date = factory.LazyFunction(date.today)
    study_type = "long_term"
    status = "active"
    shelf = factory.Sequence(lambda n: f"S{n}")
    rack = factory.Sequence(lambda n: f"R{n}")
    position = factory.Sequence(lambda n: f"P{n}")
    qty_placed = 60
    qty_remaining = 60
    created_by = factory.SubFactory(UserFactory)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        from services.schedule_engine import ScheduleEngine
        from django.db import transaction

        with transaction.atomic():
            batch = model_class.objects.create(*args, **kwargs)
            ScheduleEngine.generate(batch)
            return batch
