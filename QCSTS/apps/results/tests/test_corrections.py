import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.results.tests.factories import TestResultFactory
from apps.results.models import ResultCorrection, TestResult
from services.signature_service import SignatureService

@pytest.mark.django_db
class TestResultCorrectionWorkflow:

    def test_analyst_can_correct_result_with_reason(self):
        client = APIClient()
        original = TestResultFactory(value="50.0")
        analyst = original.analyst
        
        token = SignatureService.issue(analyst)
        client.force_authenticate(user=analyst)
        
        response = client.post(
            reverse("correct-result", kwargs={"result_id": original.id}),
            {"value": "99.5", "reason": "Transcription error."},
            HTTP_X_SIGNATURE_TOKEN=token,
            format="json"
        )
        
        assert response.status_code == 201
        
        # Original is soft-deleted
        original.refresh_from_db()
        assert original.is_active is False
        
        # New result is active
        new_result = TestResult.objects.get(test_point=original.test_point, monograph_test=original.monograph_test)
        assert new_result.value == "99.5"
        assert new_result.is_active is True
        
        # Correction record links them
        correction = ResultCorrection.objects.get(original_result=original)
        assert correction.corrected_result == new_result
        assert correction.reason == "Transcription error."

    def test_correction_requires_reason(self):
        client = APIClient()
        original = TestResultFactory()
        analyst = original.analyst
        
        token = SignatureService.issue(analyst)
        client.force_authenticate(user=analyst)
        
        response = client.post(
            reverse("correct-result", kwargs={"result_id": original.id}),
            {"value": "99.5", "reason": ""}, # Empty reason
            HTTP_X_SIGNATURE_TOKEN=token,
            format="json"
        )
        
        assert response.status_code == 400

    def test_correction_requires_signature(self):
        client = APIClient()
        original = TestResultFactory()
        analyst = original.analyst
        
        client.force_authenticate(user=analyst)
        
        # Missing X-Signature-Token header
        response = client.post(
            reverse("correct-result", kwargs={"result_id": original.id}),
            {"value": "99.5", "reason": "Typo."},
            format="json"
        )
        
        assert response.status_code == 403