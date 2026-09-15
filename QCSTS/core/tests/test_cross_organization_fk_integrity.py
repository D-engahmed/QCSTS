"""
Model-layer defense in depth: a tenant-owned record must never reference
another tenant-owned record that belongs to a different organization.

core/tests/test_serializer_tenant_scoping.py and test_tenant_isolation.py
already prove this can't happen through the API (the request/response path).
These tests prove it can't happen at all — the ORM refuses the write even
when a serializer, a view, or tenant-context resolution is not involved
(Django admin, a management command, a data migration, a future call site
that builds a model instance directly). See core/models.py:
BaseModel.assert_same_organization and doc 01-organization-ownership.md rule 4
/ 05-tenant-security-tests.md's "Relationships" matrix.

Each test builds a fully consistent record in Organization A, then swaps a
single related field for the equivalent record from Organization B and
asserts the save is rejected with a ValidationError — never persisted.
"""

import pytest
from django.core.exceptions import ValidationError

from apps.batches.models import Batch
from apps.batches.tests.factories import BatchFactory
from apps.chamber.models import LocationHistory, SamplePull
from apps.platform.models import Organization
from apps.products.models import MonographTest, Product
from apps.products.tests.factories import (
    MonographFactory,
    MonographWithTestsFactory,
    ProductFactory,
)
from apps.results.models import ResultCorrection, ResultReview, TestResult
from apps.results.tests.factories import TestResultFactory
from apps.schedule.models import TestPoint


@pytest.fixture
def two_orgs(db):
    org_a = Organization.objects.create(name="Org A", slug="fk-org-a", country="EG")
    org_b = Organization.objects.create(name="Org B", slug="fk-org-b", country="EG")
    return org_a, org_b


@pytest.mark.django_db
class TestCrossOrganizationForeignKeysAreRejected:
    def test_monograph_test_cannot_reference_another_orgs_monograph(self, two_orgs):
        org_a, org_b = two_orgs
        monograph_a = MonographFactory(organization=org_a)

        with pytest.raises(ValidationError):
            MonographTest.objects.create(
                monograph=monograph_a,
                name="Assay",
                method="HPLC",
                specification="98.0 - 102.0",
                unit="%",
                sequence=1,
                organization=org_b,
            )
        assert not MonographTest.all_objects.filter(monograph=monograph_a).exists()

    def test_product_cannot_reference_another_orgs_monograph(self, two_orgs):
        org_a, org_b = two_orgs
        monograph_a = MonographWithTestsFactory(organization=org_a)

        with pytest.raises(ValidationError):
            Product.objects.create(
                name="Amoxicillin",
                strength="500 mg",
                dosage_form="capsule",
                monograph=monograph_a,
                organization=org_b,
            )
        assert not Product.all_objects.filter(monograph=monograph_a).exists()

    def test_batch_cannot_reference_another_orgs_product(self, two_orgs):
        org_a, org_b = two_orgs
        product_a = ProductFactory(organization=org_a)

        with pytest.raises(ValidationError):
            Batch.objects.create(
                product=product_a,
                batch_number="CROSS-ORG-001",
                mfg_date="2024-01-01",
                expiry_date="2027-01-01",
                incubation_date="2024-01-01",
                study_type="long_term",
                shelf="S1",
                rack="R1",
                position="P1",
                qty_placed=10,
                qty_remaining=10,
                organization=org_b,
            )
        assert not Batch.all_objects.filter(product=product_a).exists()

    def test_test_point_cannot_reference_another_orgs_batch(self, two_orgs):
        org_a, org_b = two_orgs
        batch_a = BatchFactory(organization=org_a)

        with pytest.raises(ValidationError):
            TestPoint.objects.create(
                batch=batch_a,
                month=1,
                scheduled_date="2024-02-01",
                organization=org_b,
            )
        assert not TestPoint.all_objects.filter(batch=batch_a, month=1).exists()

    def test_sample_pull_cannot_reference_another_orgs_batch(self, two_orgs):
        org_a, org_b = two_orgs
        batch_a = BatchFactory(organization=org_a)

        with pytest.raises(ValidationError):
            SamplePull.objects.create(
                batch=batch_a,
                qty_pulled=1,
                organization=org_b,
            )
        assert not SamplePull.all_objects.filter(batch=batch_a).exists()

    def test_location_history_cannot_reference_another_orgs_batch(self, two_orgs):
        org_a, org_b = two_orgs
        batch_a = BatchFactory(organization=org_a)

        with pytest.raises(ValidationError):
            LocationHistory.objects.create(
                batch=batch_a,
                old_shelf="S1", old_rack="R1", old_position="P1",
                new_shelf="S2", new_rack="R2", new_position="P2",
                organization=org_b,
            )
        assert not LocationHistory.all_objects.filter(batch=batch_a).exists()

    def test_result_cannot_reference_another_orgs_monograph_test(self, two_orgs):
        org_a, org_b = two_orgs
        batch_a = BatchFactory(organization=org_a)
        test_point_a = batch_a.test_points.first()
        monograph_b = MonographWithTestsFactory(organization=org_b)
        monograph_test_b = monograph_b.tests.first()

        with pytest.raises(ValidationError):
            TestResult.objects.create(
                test_point=test_point_a,
                monograph_test=monograph_test_b,
                value="99.5",
                unit="%",
                specification_snapshot="98.0 - 102.0",
                organization=org_a,
            )
        assert not TestResult.all_objects.filter(test_point=test_point_a).exists()

    def test_review_cannot_reference_another_orgs_result(self, two_orgs):
        org_a, org_b = two_orgs
        result_a = TestResultFactory(batch=BatchFactory(organization=org_a))

        with pytest.raises(ValidationError):
            ResultReview.objects.create(
                result=result_a,
                action="QA_APPROVE",
                result_snapshot=result_a.build_review_snapshot(),
                organization=org_b,
            )
        assert not ResultReview.all_objects.filter(result=result_a).exists()

    def test_correction_cannot_link_results_from_different_orgs(self, two_orgs):
        org_a, org_b = two_orgs
        original_a = TestResultFactory(batch=BatchFactory(organization=org_a))
        corrected_b = TestResultFactory(batch=BatchFactory(organization=org_b))

        with pytest.raises(ValidationError):
            ResultCorrection.objects.create(
                original_result=original_a,
                corrected_result=corrected_b,
                reason="Cross-org correction attempt.",
            )
        assert not ResultCorrection.all_objects.filter(original_result=original_a).exists()
