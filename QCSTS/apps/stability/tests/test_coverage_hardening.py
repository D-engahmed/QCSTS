from unittest.mock import MagicMock, patch

import pytest
from django.core.exceptions import ValidationError
from rest_framework.test import APIRequestFactory

from apps.accounts.tests.factories import AdminFactory
from apps.platform.permissions import HasTenantContext
from apps.stability.api import (
    StabilityPermissionByAction,
    StabilityTenantViewSet,
)
from apps.stability.models import (
    ProtocolVersion, SpecificationVersion, StabilitySample,
    StabilityStudy, StorageCondition, StudyTimepoint,
)


def test_stability_allowed_transition_matrix():
    view = StabilityTenantViewSet()
    assert view.allowed_transitions(ProtocolVersion(status="draft"))["draft"] == {"approved"}
    assert view.allowed_transitions(SpecificationVersion(status="approved"))["approved"] == {"effective", "superseded"}
    assert view.allowed_transitions(StabilityStudy(status="active"))["active"] == {"completed", "canceled"}
    assert view.allowed_transitions(StudyTimepoint(status="open"))["open"] == {"completed", "canceled"}
    assert view.allowed_transitions(StabilitySample(status="testing"))["testing"] == {"completed", "disposed"}
    assert view.allowed_transitions(object()) == {}


def test_stability_permission_by_action_delegates():
    permission = StabilityPermissionByAction()
    view = MagicMock()
    request = MagicMock()
    with patch("apps.stability.api.IsViewer.has_permission", return_value=True) as check:
        view.action = "list"
        assert permission.has_permission(request, view) is True
        check.assert_called_once()
    with patch("apps.stability.api.IsAnalystOrAbove.has_permission", return_value=True):
        view.action = "create"
        assert permission.has_permission(request, view) is True
    with patch("apps.stability.api.IsReviewerOrAbove.has_permission", return_value=True):
        view.action = "update"
        assert permission.has_permission(request, view) is True
        view.action = "approve"
        assert permission.has_permission(request, view) is True
    with patch("apps.stability.api.IsAdmin.has_permission", return_value=True):
        view.action = "destroy"
        assert permission.has_permission(request, view) is True
    with patch("apps.stability.api.HasTenantContext.has_permission", return_value=True):
        view.action = "other"
        assert permission.has_permission(request, view) is True


def test_storage_condition_validation():
    condition = StorageCondition(
        code="40C", name="40C", temperature_min_c=50, temperature_max_c=40,
    )
    with patch("apps.stability.models.BaseModel.save"):
        with pytest.raises(ValidationError):
            condition.save()
    condition = StorageCondition(
        code="RH", name="Humidity", humidity_min_rh=90, humidity_max_rh=50,
    )
    with patch("apps.stability.models.BaseModel.save"):
        with pytest.raises(ValidationError):
            condition.save()


@pytest.mark.django_db
def test_stability_transition_and_soft_delete():
    user = AdminFactory()
    org = user.memberships.select_related("organization").get().organization
    factory = APIRequestFactory()
    obj = StabilityStudy(status="draft")
    view = StabilityTenantViewSet()
    view.get_object = MagicMock(return_value=obj)
    view.get_serializer = MagicMock(return_value=MagicMock(data={"status": obj.status}))
    obj.save = MagicMock()

    request = factory.post("/transition/", {"status": "planned"}, format="json")
    request.user = user
    request.organization = org
    with patch("apps.stability.api.AuditService.log"):
        response = view.transition(request, pk="1")
    assert response.status_code == 200
    assert obj.status == "planned"

    request = factory.post("/transition/", {"status": "active", "comments": "Start"}, format="json")
    request.user = user
    request.organization = org
    obj.status = "planned"
    with patch("apps.stability.api.AuditService.log"),          patch("apps.stability.api.SignatureService.validate", return_value=True),          patch("apps.stability.api.ElectronicSignature.issue"):
        request.META["HTTP_X_SIGNATURE_TOKEN"] = "sig"
        response = view.transition(request, pk="1")
    assert response.status_code == 200

    obj.soft_delete = MagicMock()
    request = factory.delete("/1/")
    request.user = user
    request.organization = org
    view.perform_destroy(obj)
    obj.soft_delete.assert_called_once()
