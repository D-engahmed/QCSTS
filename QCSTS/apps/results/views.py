from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import ScopedRateThrottle
from drf_spectacular.utils import extend_schema
from drf_spectacular.types import OpenApiTypes

from core.views import TenantScopedAPIView
from apps.results.models import TestResult, ResultReview, ResultCorrection
from apps.results.serializers import TestResultSerializer, ResultReviewSerializer, ResultCorrectionSerializer
from apps.compliance.models import ElectronicSignature, ControlledRecord
from services.signature_service import SignatureService
from services.audit_service import AuditService
from core.permissions import IsAnalystOrAbove, IsReviewerOrAbove, IsQAManager
from apps.platform.permissions import HasTenantContext
from core.responses import success_response, error_response


class VerifySignatureView(TenantScopedAPIView):
    """Re-authenticate a user and issue a short-lived one-time workflow token."""
    permission_classes = [HasTenantContext]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "signature"

    @extend_schema(operation_id="verify_signature", request=OpenApiTypes.OBJECT, responses=OpenApiTypes.OBJECT)
    def post(self, request):
        password = request.data.get("password")
        user = request.user
        if not password:
            return error_response("Password is required.", status_code=400)
        if not user.check_password(password):
            return error_response("Invalid password", status_code=401)
        return success_response({"signature_token": SignatureService.issue(user)})


class SubmitResultView(TenantScopedAPIView):
    permission_classes = [IsAuthenticated, IsAnalystOrAbove]

    @extend_schema(operation_id="result_list", responses=TestResultSerializer(many=True))
    def get(self, request):
        queryset = self.tenant_qs(TestResult.objects.select_related("test_point", "monograph_test", "analyst"))
        test_point_id = request.query_params.get("test_point")
        if test_point_id:
            queryset = queryset.filter(test_point__id=test_point_id)
        batch_id = request.query_params.get("batch")
        if batch_id:
            queryset = queryset.filter(test_point__batch__id=batch_id)
        return success_response(data=TestResultSerializer(queryset, many=True).data)

    @extend_schema(operation_id="result_submit", request=TestResultSerializer, responses=TestResultSerializer)
    def post(self, request):
        token = request.headers.get("X-Signature-Token")
        if not token or not SignatureService.validate(request.user, token):
            return error_response("Invalid or missing signature token", status_code=403)
        serializer = TestResultSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        result = serializer.save(analyst=request.user, created_by=request.user, organization=request.organization)
        return success_response(data=TestResultSerializer(result).data, status_code=201)


class SupervisorReviewResultView(TenantScopedAPIView):
    permission_classes = [IsAuthenticated, IsReviewerOrAbove]

    @transaction.atomic
    @extend_schema(operation_id="result_supervisor_review", request=OpenApiTypes.OBJECT, responses=ResultReviewSerializer)
    def post(self, request, result_id):
        token = request.headers.get("X-Signature-Token")
        if not token or not SignatureService.validate(request.user, token):
            return error_response("Invalid or missing signature token", status_code=403)
        result = get_object_or_404(
            TestResult.objects.select_related("analyst", "test_point", "monograph_test"),
            id=result_id, organization=request.organization,
        )
        if result.analyst_id == request.user.id:
            return error_response("Self-review is not permitted.", status_code=403)
        if result.workflow_state() != "submitted":
            return error_response(f"Invalid workflow transition from {result.workflow_state()} to under_review.", status_code=400)
        comments = request.data.get("comments", "")
        review = ResultReview.objects.create(
            result=result, action="SUPERVISOR_REVIEW", reviewed_by=request.user,
            comments=comments, result_snapshot=result.build_review_snapshot(),
            organization=request.organization, created_by=request.user,
        )
        signature = ElectronicSignature.issue(
            organization=request.organization, signer=request.user, record_type="TestResult",
            record_id=result.id, record_version="1", meaning=ElectronicSignature.Meaning.REVIEW,
            reason=comments.strip() or "Supervisor review decision.", authentication_secret=settings.SECRET_KEY,
        )
        AuditService.log(
            performed_by=request.user, action="UPDATE", model_name="TestResult", object_id=result.id,
            object_repr=str(result), old_value={"workflow_state": "submitted"},
            new_value={"workflow_state": "under_review", "signature_id": str(signature.id)},
            ip_address=request.META.get("REMOTE_ADDR"),
            notes="Supervisor reviewed submitted result and persisted electronic signature.",
            organization=request.organization,
        )
        return success_response(data=ResultReviewSerializer(review).data, status_code=201)


class QAApproveResultView(TenantScopedAPIView):
    permission_classes = [IsAuthenticated, IsQAManager]

    @transaction.atomic
    @extend_schema(operation_id="result_qa_approve", request=OpenApiTypes.OBJECT, responses=ResultReviewSerializer)
    def post(self, request, result_id):
        token = request.headers.get("X-Signature-Token")
        if not token or not SignatureService.validate(request.user, token):
            return error_response("Invalid or missing signature token", status_code=403)
        result = get_object_or_404(
            TestResult.objects.select_related("analyst", "test_point", "monograph_test"),
            id=result_id, organization=request.organization,
        )
        if result.analyst_id == request.user.id:
            return error_response("Self-approval is not permitted.", status_code=403)
        if result.workflow_state() != "under_review":
            return error_response(f"Invalid workflow transition from {result.workflow_state()} to approved.", status_code=400)
        comments = request.data.get("comments", "")
        review = ResultReview.objects.create(
            result=result, action="QA_APPROVE", reviewed_by=request.user,
            comments=comments, result_snapshot=result.build_review_snapshot(),
            organization=request.organization, created_by=request.user,
        )
        signature = ElectronicSignature.issue(
            organization=request.organization, signer=request.user, record_type="TestResult",
            record_id=result.id, record_version="1", meaning=ElectronicSignature.Meaning.APPROVAL,
            reason=comments.strip() or "QA approval decision.", authentication_secret=settings.SECRET_KEY,
        )
        controlled, _ = ControlledRecord.objects.get_or_create(
            organization=request.organization,
            record_type="TestResult",
            record_id=result.id,
            defaults={
                "created_by": request.user,
                "status": ControlledRecord.Status.APPROVED,
                "approved_by": request.user,
                "approved_at": __import__("django.utils.timezone", fromlist=["now"]).now(),
            },
        )
        if controlled.status != ControlledRecord.Status.LOCKED:
            controlled.status = ControlledRecord.Status.APPROVED
            controlled.approved_by = request.user
            controlled.approved_at = __import__("django.utils.timezone", fromlist=["now"]).now()
            controlled.save(update_fields=["status", "approved_by", "approved_at", "updated_at"])
            controlled.lock(request.user)

        AuditService.log(
            performed_by=request.user, action="APPROVE", model_name="TestResult", object_id=result.id,
            object_repr=str(result), old_value={"workflow_state": "under_review"},
            new_value={"workflow_state": "approved", "signature_id": str(signature.id)},
            ip_address=request.META.get("REMOTE_ADDR"),
            notes="QA approved submitted result and persisted electronic signature.",
            organization=request.organization,
        )
        return success_response(data=ResultReviewSerializer(review).data, status_code=201)


class QARejectResultView(TenantScopedAPIView):
    permission_classes = [IsAuthenticated, IsQAManager]

    @transaction.atomic
    @extend_schema(operation_id="result_qa_reject", request=OpenApiTypes.OBJECT, responses=ResultReviewSerializer)
    def post(self, request, result_id):
        token = request.headers.get("X-Signature-Token")
        if not token or not SignatureService.validate(request.user, token):
            return error_response("Invalid or missing signature token", status_code=403)
        result = get_object_or_404(
            TestResult.objects.select_related("analyst", "test_point", "monograph_test"),
            id=result_id, organization=request.organization,
        )
        if result.analyst_id == request.user.id:
            return error_response("Self-rejection is not permitted.", status_code=403)
        if result.workflow_state() != "under_review":
            return error_response(f"Invalid workflow transition from {result.workflow_state()} to rejected.", status_code=400)
        comments = request.data.get("comments", "")
        if not comments:
            return error_response("Rejection comments are required.", status_code=400)
        review = ResultReview.objects.create(
            result=result, action="QA_REJECT", reviewed_by=request.user,
            comments=comments, result_snapshot=result.build_review_snapshot(),
            organization=request.organization, created_by=request.user,
        )
        signature = ElectronicSignature.issue(
            organization=request.organization, signer=request.user, record_type="TestResult",
            record_id=result.id, record_version="1", meaning=ElectronicSignature.Meaning.REJECTION,
            reason=comments.strip(), authentication_secret=settings.SECRET_KEY,
        )
        AuditService.log(
            performed_by=request.user, action="REJECT", model_name="TestResult", object_id=result.id,
            object_repr=str(result), old_value={"workflow_state": "under_review"},
            new_value={"workflow_state": "rejected", "signature_id": str(signature.id)},
            ip_address=request.META.get("REMOTE_ADDR"),
            notes="QA rejected submitted result and persisted electronic signature.",
            organization=request.organization,
        )
        return success_response(data=ResultReviewSerializer(review).data, status_code=201)


class CorrectResultView(TenantScopedAPIView):
    permission_classes = [IsAuthenticated, IsAnalystOrAbove]

    @transaction.atomic
    @extend_schema(operation_id="result_correct", request=OpenApiTypes.OBJECT, responses=ResultCorrectionSerializer)
    def post(self, request, result_id):
        token = request.headers.get("X-Signature-Token")
        if not token or not SignatureService.validate(request.user, token):
            return error_response("Invalid or missing signature token", status_code=403)
        reason = request.data.get("reason", "").strip()
        if not reason:
            return error_response("A reason for the correction is required.", status_code=400)
        controlled = ControlledRecord.objects.filter(
            organization=request.organization,
            record_type="TestResult",
            record_id=result_id,
        ).first()
        # A locked result cannot be edited in-place. A controlled correction
        # creates a new result, soft-deactivates the original, and preserves
        # the immutable correction link and audit evidence.
        if controlled and controlled.status == ControlledRecord.Status.LOCKED and not request.data.get("value"):
            return error_response("Replacement value is required for a controlled correction.", status_code=400)
        original_result = get_object_or_404(
            TestResult.objects.select_related("test_point", "monograph_test"),
            id=result_id, organization=request.organization, is_active=True,
        )
        original_result.soft_delete(
            deleted_by=request.user, ip_address=request.META.get("REMOTE_ADDR"),
            notes=f"Superseded by correction. Reason: {reason}",
        )
        serializer = TestResultSerializer(data={
            "test_point": original_result.test_point.id,
            "monograph_test": original_result.monograph_test.id,
            "value": request.data.get("value"),
            "unit": request.data.get("unit", original_result.unit),
            "notes": request.data.get("notes", original_result.notes),
        }, context={"request": request})
        serializer.is_valid(raise_exception=True)
        corrected_result = serializer.save(analyst=request.user, created_by=request.user, organization=request.organization)
        correction = ResultCorrection.objects.create(
            original_result=original_result, corrected_result=corrected_result, reason=reason,
            corrected_by=request.user, organization=request.organization, created_by=request.user,
        )
        AuditService.log(
            performed_by=request.user, action="UPDATE", model_name="ResultCorrection", object_id=correction.id,
            object_repr=str(correction), new_value={"reason": reason, "original_id": str(original_result.id), "new_id": str(corrected_result.id)},
            ip_address=request.META.get("REMOTE_ADDR"), notes="Result corrected via GxP correction workflow.",
            organization=request.organization,
        )
        return success_response(data=ResultCorrectionSerializer(correction).data, status_code=201)
