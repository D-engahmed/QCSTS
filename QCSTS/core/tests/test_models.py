import pytest
from apps.batches.tests.factories import BatchFactory
from apps.audit.models import AuditLog
from django.contrib.auth import get_user_model

@pytest.mark.django_db
class TestBaseModelSoftDelete:
    def test_soft_delete_creates_audit_log(self):
        User = get_user_model()
        user = User.objects.create_user(email="deleter@test.com", password="pass", role="admin")
        organization = user.memberships.select_related("organization").get().organization
        batch = BatchFactory(organization=organization, created_by=user)
        
        initial_count = AuditLog.objects.count()
        
        batch.soft_delete(deleted_by=user, ip_address="127.0.0.1", notes="Testing deletion")
        
        assert batch.is_active is False
        
        # Verify audit log was created
        assert AuditLog.objects.count() == initial_count + 1
        log = AuditLog.objects.filter(model_name="Batch", object_id=str(batch.id)).first()
        
        assert log is not None
        assert log.action == "DELETE"
        assert log.performed_by == user
        assert log.organization == organization  # Tenant isolation verified
        assert log.ip_address == "127.0.0.1"
        assert log.notes == "Testing deletion"
        assert log.old_value == {"is_active": True}
        assert log.new_value == {"is_active": False}

    def test_soft_delete_without_user_still_logs(self):
        """System-initiated deletions should still be logged with performed_by=None"""
        batch = BatchFactory()
        batch.soft_delete()
        
        assert batch.is_active is False
        log = AuditLog.objects.filter(model_name="Batch", object_id=str(batch.id)).first()
        assert log is not None
        assert log.action == "DELETE"
        assert log.performed_by is None
        assert log.organization == batch.organization