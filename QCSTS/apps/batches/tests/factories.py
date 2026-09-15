import factory
from factory.django import DjangoModelFactory
from datetime import date
from apps.batches.models import Batch
from apps.accounts.tests.factories import UserFactory
from apps.products.tests.factories import ProductFactory, _default_org_for_user


class BatchFactory(DjangoModelFactory):
    class Meta:
        model = Batch

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
    # Independent of `product` so that an explicit `organization=` override
    # (with no matching `product=` override) doesn't leave `organization`
    # trying to derive from a `product` that itself needs `organization` to
    # be resolved first — that's circular. `product` instead follows
    # whichever organization this Batch ends up with, below.
    organization = factory.LazyAttribute(lambda obj: _default_org_for_user(obj.created_by))
    product = factory.SubFactory(
        ProductFactory,
        organization=factory.SelfAttribute("..organization"),
        created_by=factory.SelfAttribute("..created_by"),
    )

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        from services.schedule_engine import ScheduleEngine
        from django.db import transaction

        with transaction.atomic():
            batch = model_class.objects.create(*args, **kwargs)
            ScheduleEngine.generate(batch)
            return batch
