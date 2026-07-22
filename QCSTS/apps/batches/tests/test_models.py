import pytest
from datetime import date
from apps.batches.tests.factories import BatchFactory
from apps.schedule.models import TestPoint


@pytest.mark.django_db
class TestBatchModel:

    def test_batch_created_successfully(self):
        batch = BatchFactory()
        assert batch.id is not None
        assert batch.status == "active"

    def test_batch_str(self):
        batch = BatchFactory(batch_number="AMX-2024-001")
        assert "AMX-2024-001" in str(batch)

    def test_batch_get_location(self):
        batch = BatchFactory(shelf="S1", rack="R1", position="P1")
        assert batch.get_location() == "S1/R1/P1"

    def test_batch_has_uuid_id(self):
        batch = BatchFactory()
        assert len(str(batch.id)) == 36

    def test_qty_remaining_equals_qty_placed_on_creation(self):
        batch = BatchFactory(qty_placed=60)
        assert batch.qty_remaining == 60

    def test_schedule_engine_generates_test_points_for_long_term(self):
        batch = BatchFactory(study_type="long_term")
        test_points = TestPoint.objects.filter(batch=batch)
        assert test_points.count() == 8
        months = list(test_points.values_list("month", flat=True))
        assert sorted(months) == [0, 3, 6, 9, 12, 18, 24, 36]

    def test_schedule_engine_generates_test_points_for_accelerated(self):
        batch = BatchFactory(study_type="accelerated")
        test_points = TestPoint.objects.filter(batch=batch)
        assert test_points.count() == 3
        months = list(test_points.values_list("month", flat=True))
        assert sorted(months) == [0, 3, 6]

    def test_test_points_scheduled_dates_are_correct(self):
        today = date.today()
        batch = BatchFactory(study_type="accelerated", incubation_date=today)
        from dateutil.relativedelta import relativedelta

        tp_month_3 = TestPoint.objects.get(batch=batch, month=3)
        expected_date = today + relativedelta(months=3)
        assert tp_month_3.scheduled_date == expected_date

    def test_all_test_points_start_as_pending(self):
        batch = BatchFactory()
        statuses = TestPoint.objects.filter(batch=batch).values_list("status", flat=True)
        assert all(s == "pending" for s in statuses)
