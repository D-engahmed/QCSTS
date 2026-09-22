from unittest.mock import MagicMock, patch

import pytest
from rest_framework.test import APIRequestFactory

from apps.accounts.tests.factories import AdminFactory
from apps.quality.models import CAPA, ChangeControl, Deviation
from apps.quality.views import DeviationViewSet


@pytest.mark.django_db
def test_quality_model_save_paths_and_lifecycle_transitions():
    user = AdminFactory()
    org = user.memberships.select_related("organization").get().organization
    deviation = Deviation.objects.create(
        organization=org, created_by=user, owner=user,
        reference="DEV-COV", title="Deviation", description="Coverage",
    )
    capa = CAPA.objects.create(
        organization=org, created_by=user, owner=user,
        reference="CAPA-COV", title="CAPA", description="Coverage",
        corrective_action="Correct", preventive_action="Prevent",
    )
    change = ChangeControl.objects.create(
        organization=org, created_by=user, owner=user,
        reference="CC-COV", title="Change", description="Coverage",
        change_type="process", current_state="old", proposed_state="new",
        risk_assessment="low",
    )
    assert deviation.pk and capa.pk and change.pk

    factory = APIRequestFactory()
    view = DeviationViewSet()
    view.get_object = MagicMock(return_value=deviation)
    view.get_serializer = MagicMock(return_value=MagicMock(data={"id": str(deviation.id)}))

    def req(payload):
        raw = factory.post("/transition/", payload, format="json")
        raw.data = payload
        raw.organization = org
        raw.user = user
        return raw

    request = req({"status": "bad"})
    assert view.transition(request, pk=str(deviation.id)).status_code == 400

    request = req({"status": "investigation"})
    assert view.transition(request, pk=str(deviation.id)).status_code == 400

    with patch("apps.quality.views.AuditService.log"), patch("apps.quality.views.SignatureService.validate", return_value=True), patch("apps.quality.views.ElectronicSignature.issue"):
        response = view.transition(req({"status": "investigation", "comments": "Begin investigation"}), pk=str(deviation.id))
        assert response.status_code == 200
        response = view.transition(req({"status": "pending_approval", "comments": "Ready"}), pk=str(deviation.id))
        assert response.status_code == 200
        raw = req({"status": "approved", "comments": "Approved"})
        raw.META["HTTP_X_SIGNATURE_TOKEN"] = "valid"
        response = view.transition(raw, pk=str(deviation.id))
        assert response.status_code == 200
