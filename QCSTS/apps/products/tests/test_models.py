import pytest
from apps.products.tests.factories import (
    MonographFactory,
    ApprovedMonographFactory,
    MonographTestFactory,
    ProductFactory,
)


@pytest.mark.django_db
class TestMonograph:

    def test_monograph_created_successfully(self):
        monograph = MonographFactory()
        assert monograph.id is not None
        assert monograph.status == "draft"

    def test_monograph_str(self):
        monograph = MonographFactory(name="BP Monograph", version="2.0")
        assert str(monograph) == "BP Monograph v2.0"

    def test_is_approved_returns_true_when_approved(self):
        monograph = ApprovedMonographFactory()
        assert monograph.is_approved() is True

    def test_is_approved_returns_false_when_draft(self):
        monograph = MonographFactory()
        assert monograph.is_approved() is False

    def test_monograph_has_uuid_id(self):
        monograph = MonographFactory()
        assert len(str(monograph.id)) == 36


@pytest.mark.django_db
class TestMonographTest:

    def test_monograph_test_created_successfully(self):
        test = MonographTestFactory
