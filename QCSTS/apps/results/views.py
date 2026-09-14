from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from apps.results.models import TestResult, ResultReview, ResultCorrection
from apps.results.serializers import TestResultSerializer, ResultReviewSerializer, ResultCorrectionSerializer
from apps.platform.services import TenantContextService
from services.signature_service import SignatureService
from services.audit_service import AuditService
from core.permissions import IsAnalystOrAbove, IsReviewerOrAbove, IsQAManager
from core.responses import success_response, error_response


class VerifySignatureView(APIView):
    """
    POST /api/v1/results/signature/verify/
    Body: { "password": "user_password" }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        password = request.data.get("password")
        user = request.user

        if not password:
            return error_response("Password is required.", status_code=400)

        if not user.check_password(password):
            return error_response("Invalid password", status_code=401)

        token = SignatureService.issue(user)
        return success_response({"signature_token": token})


class SubmitResultView(APIView):
    """
    GET  /api/v1/results/
    POST /api/v1/results/
    """
    permission_classes = [IsAuthenticated, IsAnalystOrAbove]

    def get(self, request):
        queryset = TenantContextService.scope_queryset(request, TestResult.objects.select_related(
            "test_point",
            "monograph_test",
            "analyst",
        ))

        test_point_id = request.query_params.get("test_point")
        if test_point_id:
            queryset = queryset.filter(test_point__id=test_point_id)

        batch_id = request.query_params.get("batch")
        if batch_id:
            queryset = queryset.filter(test_point__batch__id=batch_id)

        return success_response(data=TestResultSerializer(queryset, many=True).data)

    def post(self, request):
        TenantContextService.resolve(request)
        token = request.headers.get("X-Signature-Token")
        if not token or not SignatureService.validate(request.user, token):
            return error_response("Invalid or missing signature token", status_code=403)

        serializer = TestResultSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        result = serializer.save(
            analyst=request.user,
            created_by=request.user,
            organization=request.organization,
        )
        return success_response(
            data=TestResultSerializer(result).data,
            status_code=201,
        )


class SupervisorReviewResultView(APIView):
    """
    POST /api/v1/results/<result_id>/review/
    Transition: submitted -> under_review
    """
    permission_classes = [IsAuthenticated, IsReviewerOrAbove]

    def post(self, request, result_id):
        TenantContextService.resolve(request)

        token = request.headers.get("X-Signature-Token")
        if not token or not SignatureService.validate(request.user, token):
            return error_response("Invalid or missing signature token", status_code=403)

        result = get_object_or_404(
            TestResult.objects.select_related("analyst", "test_point", "monograph_test"),
            id=result_id,
            organization=request.organization,
        )

        if result.analyst_id == request.user.id:
            return error_response("Self-review is not permitted.", status_code=403)

        current_state = result.workflow_state()
        if current_state != "submitted":
            return error_response(
                f"Invalid workflow transition from {current_state} to under_review.",
                status_code=400,
            )

        review = ResultReview.objects.create(
            result=result,
            action="SUPERVISOR_REVIEW",
            reviewed_by=request.user,
            comments=request.data.get("comments", ""),
            result_snapshot=result.build_review_snapshot(),
            organization=request.organization,
            created_by=request.user,
        )

        AuditService.log(
            performed_by=request.user,
            action="UPDATE",
            model_name="TestResult",
            object_id=result.id,
            object_repr=str(result),
            old_value={"workflow_state": "submitted"},
            new_value={"workflow_state": "under_review"},
            ip_address=request.META.get("REMOTE_ADDR"),
            notes="Supervisor reviewed submitted result.",
            organization=request.organization,
        )

        return success_response(
            data=ResultReviewSerializer(review).data,
            status_code=201,
        )


class QAApproveResultView(APIView):
    """
    POST /api/v1/results/<result_id>/approve/
    Transition: under_review -> approved
    """
    permission_classes = [IsAuthenticated, IsQAManager]

    def post(self, request, result_id):
        TenantContextService.resolve(request)

        token = request.headers.get("X-Signature-Token")
        if not token or not SignatureService.validate(request.user, token):
            return error_response("Invalid or missing signature token", status_code=403)

        result = get_object_or_404(
            TestResult.objects.select_related("analyst", "test_point", "monograph_test"),
            id=result_id,
            organization=request.organization,
        )

        if result.analyst_id == request.user.id:
            return error_response("Self-approval is not permitted.", status_code=403)

        current_state = result.workflow_state()
        if current_state != "under_review":
            return error_response(
                f"Invalid workflow transition from {current_state} to approved.",
                status_code=400,
            )

        review = ResultReview.objects.create(
            result=result,
            action="QA_APPROVE",
            reviewed_by=request.user,
            comments=request.data.get("comments", ""),
            result_snapshot=result.build_review_snapshot(),
            organization=request.organization,
            created_by=request.user,
        )

        AuditService.log(
            performed_by=request.user,
            action="APPROVE",
            model_name="TestResult",
            object_id=result.id,
            object_repr=str(result),
            old_value={"workflow_state": "under_review"},
            new_value={"workflow_state": "approved"},
            ip_address=request.META.get("REMOTE_ADDR"),
            notes="QA approved submitted result.",
            organization=request.organization,
        )

        return success_response(
            data=ResultReviewSerializer(review).data,
            status_code=201,
        )


class QARejectResultView(APIView):
    """
    POST /api/v1/results/<result_id>/reject/
    Transition: under_review -> rejected
    """
    permission_classes = [IsAuthenticated, IsQAManager]

    def post(self, request, result_id):
        TenantContextService.resolve(request)

        token = request.headers.get("X-Signature-Token")
        if not token or not SignatureService.validate(request.user, token):
            return error_response("Invalid or missing signature token", status_code=403)

        result = get_object_or_404(
            TestResult.objects.select_related("analyst", "test_point", "monograph_test"),
            id=result_id,
            organization=request.organization,
        )

        if result.analyst_id == request.user.id:
            return error_response("Self-rejection is not permitted.", status_code=403)

        current_state = result.workflow_state()
        if current_state != "under_review":
            return error_response(
                f"Invalid workflow transition from {current_state} to rejected.",
                status_code=400,
            )

        comments = request.data.get("comments", "")
        if not comments:
            return error_response("Rejection comments are required.", status_code=400)

        review = ResultReview.objects.create(
            result=result,
            action="QA_REJECT",
            reviewed_by=request.user,
            comments=comments,
            result_snapshot=result.build_review_snapshot(),
            organization=request.organization,
            created_by=request.user,
        )

        AuditService.log(
            performed_by=request.user,
            action="REJECT",
            model_name="TestResult",
            object_id=result.id,
            object_repr=str(result),
            old_value={"workflow_state": "under_review"},
            new_value={"workflow_state": "rejected"},
            ip_address=request.META.get("REMOTE_ADDR"),
            notes="QA rejected submitted result.",
            organization=request.organization,
        )

        return success_response(
            data=ResultReviewSerializer(review).data,
            status_code=201,
        )

class CorrectResultView(APIView):
    """
    POST /api/v1/results/<result_id>/correct/
    Header: X-Signature-Token: <token>
    Body: {
        "value": "99.8",
        "unit": "%",
        "reason": "Typo in original transcription. Verified against lab notebook."
    }
    """
    permission_classes = [IsAuthenticated, IsAnalystOrAbove]

    def post(self, request, result_id):
        TenantContextService.resolve(request)

        token = request.headers.get("X-Signature-Token")
        if not token or not SignatureService.validate(request.user, token):
            return error_response("Invalid or missing signature token", status_code=403)

        reason = request.data.get("reason", "").strip()
        if not reason:
            return error_response("A reason for the correction is required.", status_code=400)

        # Fetch the active original result
        original_result = get_object_or_404(
            TestResult.objects.select_related("test_point", "monograph_test"),
            id=result_id,
            organization=request.organization,
            is_active=True
        )

        # 1. Soft-delete the original result (preserves history)
        original_result.soft_delete(
            deleted_by=request.user,
            ip_address=request.META.get("REMOTE_ADDR"),
            notes=f"Superseded by correction. Reason: {reason}"
        )

        # 2. Create the new corrected result
        new_data = {
            "test_point": original_result.test_point.id,
            "monograph_test": original_result.monograph_test.id,
            "value": request.data.get("value"),
            "unit": request.data.get("unit", original_result.unit),
            "notes": request.data.get("notes", original_result.notes),
        }
        
        serializer = TestResultSerializer(data=new_data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        
        corrected_result = serializer.save(
            analyst=request.user,
            created_by=request.user,
            organization=request.organization,
        )

        # 3. Create the immutable correction record
        correction = ResultCorrection.objects.create(
            original_result=original_result,
            corrected_result=corrected_result,
            reason=reason,
            corrected_by=request.user,
            organization=request.organization,
            created_by=request.user,
        )

        AuditService.log(
            performed_by=request.user,
            action="UPDATE", 
            model_name="ResultCorrection",
            object_id=correction.id,
            object_repr=str(correction),
            new_value={"reason": reason, "original_id": str(original_result.id), "new_id": str(corrected_result.id)},
            ip_address=request.META.get("REMOTE_ADDR"),
            notes="Result corrected via GxP correction workflow.",
            organization=request.organization,
        )

        return success_response(
            data=ResultCorrectionSerializer(correction).data,
            status_code=201,
        )