import factory
from factory.django import DjangoModelFactory
from apps.audit.models import AuditLog
from apps.accounts.tests.factories import UserFactory


class AuditLogFactory(DjangoModelFactory):
    class Meta:
        model = AuditLog

    performed_by = factory.SubFactory(UserFactory)
    action = "CREATE"
    model_name = "Batch"
    object_id = factory.Faker("uuid4")
    object_repr = "Batch AMX-2024-001"
    old_value = None
    new_value = {"status": "active"}
    ip_address = "127.0.0.1"
    notes = ""
