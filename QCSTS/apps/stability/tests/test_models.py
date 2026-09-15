from datetime import date

import pytest
from django.core.exceptions import ValidationError

from apps.batches.models import Batch
from apps.platform.models import Organization, Site
from apps.products.models import Product
from apps.stability.models import (
    Protocol,
    ProtocolVersion,
    Specification,
    SpecificationVersion,
    StabilityStudy,
    StudyBatch,
    StudyTimepoint,
    StorageCondition,
    StabilitySample,
)


@pytest.fixture
def organization(db):
    return Organization.objects.create(name="Acme Pharma", slug="acme-pharma", country="EG")


@pytest.fixture
def site(organization):
    return Site.objects.create(organization=organization, name="Cairo QC", country="EG")


@pytest.fixture
def product(organization):
    return Product.objects.create(
        organization=organization,
        name="Example Tablets",
        strength="500 mg",
        dosage_form="tablet",
    )


def test_protocol_and_version_are_tenant_scoped(organization, product):
    protocol = Protocol.objects.create(
        organization=organization,
        code="STAB-LT-001",
        name="Long-term stability",
        product=product,
        study_type="long_term",
    )
    version = ProtocolVersion.objects.create(
        organization=organization,
        protocol=protocol,
        version="1.0",
    )

    assert version.protocol_id == protocol.id
    assert version.organization_id == organization.id


def test_protocol_rejects_cross_tenant_product(db, product):
    other_org = Organization.objects.create(name="Other Pharma", slug="other-pharma", country="EG")
    protocol = Protocol(
        organization=other_org,
        code="STAB-001",
        name="Invalid protocol",
        product=product,
        study_type="long_term",
    )

    with pytest.raises(ValidationError):
        protocol.save()


def test_specification_version_is_independent_of_current_specification_changes(organization, product):
    specification = Specification.objects.create(
        organization=organization,
        code="ASSAY-001",
        name="Assay specification",
        product=product,
    )
    version = SpecificationVersion.objects.create(
        organization=organization,
        specification=specification,
        version="1.0",
        effective_date=date(2026, 1, 1),
    )

    specification.name = "Assay specification - revised"
    specification.save()

    version.refresh_from_db()
    assert version.version == "1.0"
    assert version.effective_date == date(2026, 1, 1)


def test_study_requires_matching_product_and_site(organization, site, product):
    protocol = Protocol.objects.create(
        organization=organization,
        code="STAB-LT-001",
        name="Long-term stability",
        product=product,
        study_type="long_term",
    )
    protocol_version = ProtocolVersion.objects.create(
        organization=organization,
        protocol=protocol,
        version="1.0",
    )

    study = StabilityStudy.objects.create(
        organization=organization,
        code="STUDY-001",
        name="Example long-term study",
        site=site,
        product=product,
        protocol_version=protocol_version,
        study_type="long_term",
    )

    assert study.status == StabilityStudy.Status.DRAFT


def test_sample_cannot_mix_study_batch_and_timepoint_from_different_studies(organization, site, product):
    protocol = Protocol.objects.create(
        organization=organization,
        code="STAB-LT-001",
        name="Long-term stability",
        product=product,
        study_type="long_term",
    )
    pv = ProtocolVersion.objects.create(organization=organization, protocol=protocol, version="1.0")
    study_a = StabilityStudy.objects.create(
        organization=organization, code="STUDY-A", name="A", site=site, product=product,
        protocol_version=pv, study_type="long_term"
    )
    study_b = StabilityStudy.objects.create(
        organization=organization, code="STUDY-B", name="B", site=site, product=product,
        protocol_version=pv, study_type="long_term"
    )
    timepoint_a = StudyTimepoint.objects.create(
        organization=organization, study=study_a, code="T0", nominal_days=0, target_date=date(2026, 1, 1)
    )
    batch = Batch.objects.create(
        organization=organization, product=product, batch_number="B-001",
        mfg_date=date(2025, 1, 1), expiry_date=date(2027, 1, 1), incubation_date=date(2025, 1, 1),
        study_type="long_term", shelf="1", rack="1", position="1", qty_placed=10, qty_remaining=10,
    )
    enrollment_b = StudyBatch.objects.create(organization=organization, study=study_b, batch=batch)
    storage = StorageCondition.objects.create(
        organization=organization, code="25C-60RH", name="25°C / 60% RH",
        temperature_min_c=25, temperature_max_c=25, humidity_min_rh=60, humidity_max_rh=60,
    )

    sample = StabilitySample(
        organization=organization,
        sample_code="S-001",
        study=study_b,
        study_batch=enrollment_b,
        timepoint=timepoint_a,
        storage_condition=storage,
        quantity=1,
    )

    with pytest.raises(ValidationError):
        sample.save()
