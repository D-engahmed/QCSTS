import pytest
from apps.audit.tests.factories import AuditLogFactory


@pytest.mark.django_db
class TestAuditLog:

    def test_audit_log_created_successfully(self):
        log = AuditLogFactory()
        assert log.id is not None
        assert log.action == "CREATE"
        assert log.model_name == "Batch"

    def test_audit_log_cannot_be_modified(self):
        log = AuditLogFactory()
        log.action = "UPDATE"
        with pytest.raises(PermissionError):
            log.save()

    def test_audit_log_cannot_be_deleted(self):
        log = AuditLogFactory()
        with pytest.raises(PermissionError):
            log.delete()

    def test_audit_log_str(self):
        log = AuditLogFactory()
        assert "CREATE" in str(log)
        assert "Batch" in str(log)

    def test_audit_log_has_timestamp(self):
        log = AuditLogFactory()
        assert log.timestamp is not None

    def test_audit_log_performed_by_can_be_null(self):
        log = AuditLogFactory(performed_by=None)
        assert log.performed_by is None
