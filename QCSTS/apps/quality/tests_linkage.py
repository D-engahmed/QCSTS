import pytest
from django.core.exceptions import ValidationError

from apps.platform.models import Organization
from apps.batches.models import Batch
from apps.schedule.models import TestPoint
from apps.quality.models import CAPA, Deviation


@pytest.fixture
def org(db):
    return Organization.objects.create(name="Acme Pharma", slug="acme-quality", country="EG")


def test_deviation_can_link_to_oos(db, org):
    oos = __import__("apps.quality.models", fromlist=["OOSInvestigation"]).OOSInvestigation
    product = __import__("apps.products.models", fromlist=["Product"]).Product.objects.create(
        organization=org,
        name="Example",
        strength="500 mg",
        dosage_form="tablet",
    )
    protocol = __import__("apps.stability.models", fromlist=["Protocol"]).Protocol.objects.create(
        organization=org, code="P-1", name="Protocol", product=product, study_type="long_term"
    )
    pv = __import__("apps.stability.models", fromlist=["ProtocolVersion"]).ProtocolVersion.objects.create(
        organization=org, protocol=protocol, version="1.0"
    )
    mt = __import__("apps.products.models", fromlist=["Monograph"]).Monograph.objects.create(
        organization=org, name="USP Example", version="1", effective_date="2026-01-01"
    )
    mtest = __import__("apps.products.models", fromlist=["MonographTest"]).MonographTest.objects.create(
        organization=org, monograph=mt, name="Assay", method="HPLC", specification="95-105", unit="%", sequence=1
    )
    result = __import__("apps.results.models", fromlist=["TestResult"]).TestResult.objects.create(
        organization=org, test_point=schedule_tp, monograph_test=mtest, value="110", unit="%", specification_snapshot="95-105", analyst=__import__("apps.accounts.models", fromlist=["CustomUser"]).CustomUser.objects.create_user(
            email="quality@acme.test", password="password-123", full_name="Quality Analyst", role="analyst"
        ),
    )
    finding = oos.objects.create(
        organization=org,
        reference="OOS-001",
        title="Assay OOS",
        description="Assay exceeded specification.",
        result=result,
    )
    deviation = Deviation.objects.create(
        organization=org,
        reference="DEV-001",
        title="Assay deviation",
        description="Investigation identified a process deviation.",
        source_oos=finding,
    )
    capa = CAPA.objects.create(
        organization=org,
        reference="CAPA-001",
        title="Corrective action",
        description="Corrective and preventive action.",
        corrective_action="Investigate root cause",
        source_deviation=deviation,
    )

    assert deviation.source_oos_id == finding.id
    assert capa.source_deviation_id == deviation.id


def test_quality_links_reject_cross_tenant_reference(db):
    Org = Organization
    org_a = Org.objects.create(name="A", slug="quality-a", country="EG")
    org_b = Org.objects.create(name="B", slug="quality-b", country="EG")
    deviation = Deviation.objects.create(
        organization=org_a,
        reference="DEV-A",
        title="Deviation",
        description="Deviation",
    )
    capa = CAPA(
        organization=org_b,
        reference="CAPA-B",
        title="CAPA",
        description="CAPA",
        corrective_action="Fix",
        source_deviation=deviation,
    )

    with pytest.raises(ValidationError):
        capa.save()
