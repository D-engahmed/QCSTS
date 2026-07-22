import pytest
from datetime import date, timedelta
from freezegun import freeze_time
from apps.schedule.models import TestPoint
from apps.schedule.tests.factories import TestPointFactory
from apps.batches.tests.factories import BatchFactory


@pytest.mark.django_db
class TestTestPointModel:

    def test_test_point_created_successfully(self):
        batch = BatchFactory()
        tp = TestPoint.objects.filter(batch=batch).first()
        assert tp is not None
        assert tp.status == "pending"

    def test_test_point_str(self):
        batch = BatchFactory()
        tp = TestPoint.objects.filter(batch=batch).first()
        assert batch.batch_number in str(tp)
        assert "Month" in str(tp)

    def test_is_overdue_returns_true_when_past_due(self):
        batch = BatchFactory()
        tp = TestPoint.objects.filter(batch=batch).first()
        tp.scheduled_date = date.today() - timedelta(days=1)
        tp.save()
        assert tp.is_overdue() is True

    def test_is_overdue_returns_false_when_not_past_due(self):
        batch = BatchFactory()
        tp = TestPoint.objects.filter(batch=batch).first()
        tp.scheduled_date = date.today() + timedelta(days=30)
        tp.save()
        assert tp.is_overdue() is False

    def test_is_overdue_returns_false_when_completed(self):
        batch = BatchFactory()
        tp = TestPoint.objects.filter(batch=batch).first()
        tp.scheduled_date = date.today() - timedelta(days=1)
        tp.status = "completed"
        tp.save()
        assert tp.is_overdue() is False
