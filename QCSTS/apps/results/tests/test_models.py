import pytest
from apps.results.models import TestResult
from apps.batches.tests.factories import BatchFactory
from apps.products.tests.factories import MonographTestFactory
from apps.schedule.models import TestPoint


@pytest.mark.django_db
class TestTestResultModel:

    def test_result_cannot_be_modified(self):
        batch = BatchFactory()
        tp = TestPoint.objects.filter(batch=batch).first()
        monograph_test = batch.product.monograph.tests.first()

        result = TestResult.objects.create(
            test_point=tp,
            monograph_test=monograph_test,
            value="99.5",
            unit="%",
            specification_snapshot="98.0 - 102.0",
            pass_fail="pass",
            created_by=batch.created_by,
        )

        result.value = "50.0"
        with pytest.raises(PermissionError):
            result.save()

    def test_result_str(self):
        batch = BatchFactory()
        tp = TestPoint.objects.filter(batch=batch).first()
        monograph_test = batch.product.monograph.tests.first()

        result = TestResult.objects.create(
            test_point=tp,
            monograph_test=monograph_test,
            value="99.5",
            unit="%",
            specification_snapshot="98.0 - 102.0",
            pass_fail="pass",
            created_by=batch.created_by,
        )

        assert "99.5" in str(result)
        assert "pass" in str(result)
