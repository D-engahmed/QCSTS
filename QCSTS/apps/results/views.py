from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsAnalystOrAbove
from core.responses import success_response, error_response
from apps.results.models import TestResult
from apps.results.serializers import TestResultSerializer
from services.signature_service import SignatureService


class VerifySignatureView(APIView):
    serializer_class = TestResultSerializer

    """
    POST /api/v1/results/signature/verify/
    Body: { "password": "user_password" }
    Returns: { "signature_token": "uuid" }
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
    serializer_class = TestResultSerializer

    """
    POST /api/v1/results/
    Header: X-Signature-Token: <token>
    Body: {
        "test_point": "uuid",
        "monograph_test": "uuid",
        "value": "99.5",
        "unit": "%",
        "notes": "optional"
    }
    """
    permission_classes = [IsAuthenticated, IsAnalystOrAbove]

    def get(self, request):
        queryset = TestResult.objects.select_related(
            "test_point",
            "monograph_test",
            "analyst",
        ).all()

        test_point_id = request.query_params.get("test_point")
        if test_point_id:
            queryset = queryset.filter(test_point__id=test_point_id)

        return success_response(data=TestResultSerializer(queryset, many=True).data)

    def post(self, request):
        token = request.headers.get("X-Signature-Token")
        if not token or not SignatureService.validate(request.user, token):
            return error_response("Invalid or missing signature token", status_code=403)

        serializer = TestResultSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save(
            analyst=request.user,
            created_by=request.user,
        )
        return success_response(
            data=TestResultSerializer(result).data,
            status_code=201,
        )
