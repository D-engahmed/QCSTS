import pytest
from datetime import timedelta
from django.utils import timezone
from apps.schedule.tasks import mark_overdue_test_points
from apps.schedule.models import TestPoint
from apps.batches.tests.factories import BatchFactory
from apps.audit.models import AuditLog

@pytest.mark.django_db
class TestMarkOverdueTestPointsTask:
    
    def test_marks_overdue_and_updates_batch_status(self):
        # Create a batch with a test point scheduled in the past
        batch = BatchFactory()
        tp = TestPoint.objects.filter(batch=batch).first()
        tp.scheduled_date = timezone.now().date() - timedelta(days=5)
        tp.status = "pending"
        tp.save()
        
        # Run the task
        count = mark_overdue_test_points()
        
        assert count >= 1
        tp.refresh_from_db()
        assert tp.status == "overdue"
        
    def test_automated_status_transition_is_audited(self):
        # Setup a batch where ALL test points will fail
        batch = BatchFactory()
        test_points = TestPoint.objects.filter(batch=batch)
        
        # Make them all overdue and failed
        for tp in test_points:
            tp.scheduled_date = timezone.now().date() - timedelta(days=5)
            tp.status = "failed" 
            tp.save()
            
        # Reset batch status to active to force a transition
        batch.status = "active"
        batch.save()
        
        initial_logs = AuditLog.objects.count()
        
        # Trigger the update manually to test the audit logic
        batch.update_status_from_test_points(triggered_by=None)
        
        assert AuditLog.objects.count() == initial_logs + 1
        log = AuditLog.objects.filter(model_name="Batch", object_id=str(batch.id)).latest("timestamp")
        
        assert log.action == "UPDATE"
        assert log.performed_by is None  # System action
        assert log.old_value == {"status": "active"}
        assert log.new_value == {"status": "failed"}
        assert log.organization == batch.organization