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

    request = factory.post("/transition/", {"status": "bad"}, format="json")
    request.user = user
    request.organization = org
    assert view.transition(request, pk=str(deviation.id)).status_code == 400

    request = factory.post("/transition/", {"status": "investigation"}, format="json")
    request.user = user
    request.organization = org
    assert view.transition(request, pk=str(deviation.id)).status_code == 400

    with patch("apps.quality.views.AuditService.log"),          patch("apps.quality.views.SignatureService.validate", return_value=True),          patch("apps.quality.views.ElectronicSignature.issue"):
        request = factory.post(
            "/transition/", {"status": "investigation", "comments": "Begin investigation"}, format="json"
        )
        request.user = user
        request.organization = org
        response = view.transition(request, pk=str(deviation.id))
        assert response.status_code == 200

        request = factory.post(
            "/transition/", {"status": "pending_approval", "comments": "Ready for review"}, format="json"
        )
        request.user = user
        request.organization = org
        response = view.transition(request, pk=str(deviation.id))
        assert response.status_code == 200

        request = factory.post(
            "/transition/", {"status": "approved", "comments": "Approved"}, format="json"
        )
        request.user = user
        request.organization = org
        request.META["HTTP_X_SIGNATURE_TOKEN"] = "valid"
        response = view.transition(request, pk=str(deviation.id))
        assert response.status_code == 200
