import base64
import secrets
from urllib.parse import quote

from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import ScopedRateThrottle
from drf_spectacular.utils import extend_schema
from drf_spectacular.types import OpenApiTypes

from apps.accounts.models import CustomUser
from apps.accounts.serializers import MFACodeSerializer, MFADisableSerializer
from core.responses import error_response, success_response
from core.views import TenantExemptAPIView
from services.audit_service import AuditService


def new_totp_secret():
    return base64.b32encode(secrets.token_bytes(20)).decode().rstrip("=")


class MFAStatusView(TenantExemptAPIView):
    """MFA status is user-account scoped, so it intentionally bypasses organization tenancy."""
    permission_classes = [IsAuthenticated]

    @extend_schema(operation_id="mfa_status", responses=OpenApiTypes.OBJECT)
    def get(self, request):
        return success_response(data={"enabled": request.user.mfa_enabled})


class MFASetupView(TenantExemptAPIView):
    """MFA setup is user-account scoped, so it intentionally bypasses organization tenancy."""
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "signature"

    @extend_schema(operation_id="mfa_setup", request=None, responses=OpenApiTypes.OBJECT)
    def post(self, request):
        if request.user.mfa_enabled:
            return error_response({"detail": "MFA is already enabled."}, status=400)
        secret = new_totp_secret()
        request.user.set_mfa_secret(secret)
        request.user.save(update_fields=["mfa_secret_encrypted"])
        account = quote(request.user.email, safe="")
        issuer = quote("QCSTS", safe="")
        uri = f"otpauth://totp/{issuer}:{account}?secret={secret}&issuer={issuer}&algorithm=SHA1&digits=6&period=30"
        AuditService.log(
            performed_by=request.user,
            action="MFA_SETUP_STARTED",
            model_name="CustomUser",
            object_id=request.user.id,
            object_repr=str(request.user),
        )
        return success_response(data={"secret": secret, "otpauth_uri": uri})


class MFAConfirmView(TenantExemptAPIView):
    """MFA confirmation is user-account scoped, so it intentionally bypasses organization tenancy."""
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "signature"

    @extend_schema(operation_id="mfa_confirm", request=MFACodeSerializer, responses=OpenApiTypes.OBJECT)
    def post(self, request):
        serializer = MFACodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if request.user.mfa_enabled:
            return error_response({"detail": "MFA is already enabled."}, status=400)
        if not request.user.verify_totp(serializer.validated_data["code"]):
            return error_response({"detail": "Invalid MFA code."}, status=400)
        request.user.mfa_enabled = True
        request.user.save(update_fields=["mfa_enabled"])
        AuditService.log(
            performed_by=request.user,
            action="MFA_ENABLED",
            model_name="CustomUser",
            object_id=request.user.id,
            object_repr=str(request.user),
        )
        return success_response(data={"enabled": True})


class MFADisableView(TenantExemptAPIView):
    """MFA disablement is user-account scoped, so it intentionally bypasses organization tenancy."""
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "signature"

    @extend_schema(operation_id="mfa_disable", request=MFADisableSerializer, responses=OpenApiTypes.OBJECT)
    def post(self, request):
        serializer = MFADisableSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not request.user.mfa_enabled:
            return error_response({"detail": "MFA is not enabled."}, status=400)
        if not request.user.check_password(serializer.validated_data["password"]):
            return error_response({"detail": "Current password is incorrect."}, status=400)
        if not request.user.verify_totp(serializer.validated_data["code"]):
            return error_response({"detail": "Invalid MFA code."}, status=400)
        request.user.mfa_enabled = False
        request.user.mfa_secret_encrypted = ""
        request.user.save(update_fields=["mfa_enabled", "mfa_secret_encrypted"])
        AuditService.log(
            performed_by=request.user,
            action="MFA_DISABLED",
            model_name="CustomUser",
            object_id=request.user.id,
            object_repr=str(request.user),
        )
        return success_response(data={"enabled": False})
