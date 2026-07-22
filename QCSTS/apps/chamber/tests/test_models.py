import pytest
from apps.chamber.tests.factories import SamplePullFactory, LocationHistoryFactory
from apps.batches.tests.factories import BatchFactory


@pytest.mark.django_db
class TestSamplePull:

    def test_sample_pull_created_successfully(self):
        pull = SamplePullFactory()
        assert pull.id is not None
        assert pull.qty_pulled == 5

    def test_sample_pull_str(self):
        pull = SamplePullFactory()
        assert pull.batch.batch_number in str(pull)

    def test_sample_pull_has_uuid_id(self):
        pull = SamplePullFactory()
        assert len(str(pull.id)) == 36


@pytest.mark.django_db
class TestLocationHistory:

    def test_location_history_created_successfully(self):
        history = LocationHistoryFactory()
        assert history.id is not None
        assert history.new_shelf == "S2"

    def test_location_history_str(self):
        history = LocationHistoryFactory()
        assert history.batch.batch_number in str(history)
