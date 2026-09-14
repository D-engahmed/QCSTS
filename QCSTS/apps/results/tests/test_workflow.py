import pytest
from django.urls import reverse
from rest_framework.test import APIClient  # <-- IMPORTED APIClient

from apps.results.tests.factories import TestResultFactory
from apps.audit.models import AuditLog
from apps.results.models import ResultReview
from services.signature_service import SignatureService
from apps.accounts.tests.factories import UserFactory, QAManagerFactory


@pytest.mark.django_db
class TestResultQAWorkflow:

    def test_supervisor_can_review_submitted_result(self):
        client = APIClient()  # <-- INSTANTIATE APIClient
        result = TestResultFactory()
        supervisor = UserFactory(role="supervisor")

        token = SignatureService.issue(supervisor)

        client.force_authenticate(user=supervisor)
        response = client.post(
            reverse("review-result", kwargs={"result_id": result.id}),
            {"comments": "Supervisor reviewed."},
            HTTP_X_SIGNATURE_TOKEN=token,
            format="json"
        )

        assert response.status_code == 201
        assert ResultReview.objects.filter(
            result=result,
            action="SUPERVISOR_REVIEW",
            reviewed_by=supervisor,
        ).exists()

        assert result.workflow_state() == "under_review"

    def test_qa_can_approve_after_supervisor_review(self):
        client = APIClient()
        result = TestResultFactory()
        supervisor = UserFactory(role="supervisor")
        qa = QAManagerFactory()

        ResultReview.objects.create(
            result=result,
            action="SUPERVISOR_REVIEW",
            reviewed_by=supervisor,
            comments="Reviewed.",
            result_snapshot=result.build_review_snapshot(),
            organization=result.organization,
        )

        token = SignatureService.issue(qa)

        client.force_authenticate(user=qa)
        response = client.post(
            reverse("approve-result", kwargs={"result_id": result.id}),
            {"comments": "Approved."},
            HTTP_X_SIGNATURE_TOKEN=token,
            format="json"
        )

        assert response.status_code == 201
        assert result.workflow_state() == "approved"

        assert ResultReview.objects.filter(
            result=result,
            action="QA_APPROVE",
            reviewed_by=qa,
        ).exists()

        assert AuditLog.objects.filter(
            model_name="TestResult",
            object_id=str(result.id),
            action="APPROVE",
            organization=result.organization,
        ).exists()

    def test_qa_cannot_approve_before_supervisor_review(self):
        client = APIClient()
        result = TestResultFactory()
        qa = QAManagerFactory()

        token = SignatureService.issue(qa)

        client.force_authenticate(user=qa)
        response = client.post(
            reverse("approve-result", kwargs={"result_id": result.id}),
            {"comments": "Approved."},
            HTTP_X_SIGNATURE_TOKEN=token,
            format="json"
        )

        assert response.status_code == 400
        assert not ResultReview.objects.filter(result=result, action="QA_APPROVE").exists()

    def test_self_approval_is_blocked(self):
        client = APIClient()
        result = TestResultFactory()
        analyst = result.analyst
        analyst.role = "qa_manager"
        analyst.save(update_fields=["role"])

        ResultReview.objects.create(
            result=result,
            action="SUPERVISOR_REVIEW",
            reviewed_by=UserFactory(role="supervisor"),
            comments="Reviewed.",
            result_snapshot=result.build_review_snapshot(),
            organization=result.organization,
        )

        token = SignatureService.issue(analyst)

        client.force_authenticate(user=analyst)
        response = client.post(
            reverse("approve-result", kwargs={"result_id": result.id}),
            {"comments": "Trying self approval."},
            HTTP_X_SIGNATURE_TOKEN=token,
            format="json"
        )

        assert response.status_code == 403
        assert not ResultReview.objects.filter(result=result, action="QA_APPROVE").exists()

    def test_qa_can_reject_after_supervisor_review(self):
        client = APIClient()
        result = TestResultFactory()
        supervisor = UserFactory(role="supervisor")
        qa = QAManagerFactory()

        ResultReview.objects.create(
            result=result,
            action="SUPERVISOR_REVIEW",
            reviewed_by=supervisor,
            comments="Reviewed.",
            result_snapshot=result.build_review_snapshot(),
            organization=result.organization,
        )

        token = SignatureService.issue(qa)

        client.force_authenticate(user=qa)
        response = client.post(
            reverse("reject-result", kwargs={"result_id": result.id}),
            {"comments": "Rejected due to documentation issue."},
            HTTP_X_SIGNATURE_TOKEN=token,
            format="json"
        )

        assert response.status_code == 201
        assert result.workflow_state() == "rejected"

        assert ResultReview.objects.filter(
            result=result,
            action="QA_REJECT",
            reviewed_by=qa,
        ).exists()

    def test_rejected_result_cannot_be_approved_later(self):
        client = APIClient()
        result = TestResultFactory()
        qa = QAManagerFactory()

        ResultReview.objects.create(
            result=result,
            action="SUPERVISOR_REVIEW",
            reviewed_by=UserFactory(role="supervisor"),
            comments="Reviewed.",
            result_snapshot=result.build_review_snapshot(),
            organization=result.organization,
        )

        ResultReview.objects.create(
            result=result,
            action="QA_REJECT",
            reviewed_by=qa,
            comments="Rejected.",
            result_snapshot=result.build_review_snapshot(),
            organization=result.organization,
        )

        token = SignatureService.issue(qa)

        client.force_authenticate(user=qa)
        response = client.post(
            reverse("approve-result", kwargs={"result_id": result.id}),
            {"comments": "Trying to approve after rejection."},
            HTTP_X_SIGNATURE_TOKEN=token,
            format="json"
        )

        assert response.status_code == 400
        assert result.workflow_state() == "rejected"