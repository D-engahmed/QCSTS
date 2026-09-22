from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework.permissions import AllowAny
from rest_framework.throttling import AnonRateThrottle

from apps.accounts.models import CustomUser, EmailVerificationToken
from apps.accounts.security import revoke_user_sessions
from apps.accounts.serializers import PasswordResetRequestSerializer, PasswordResetConfirmSerializer, VerifyEmailSerializer
from core.responses import error_response, success_response
from core.views import PublicAPIView
from services.audit_service import AuditService
import hashlib
import secrets
from datetime import timedelta


def _frontend_url(path):
    return f"{getattr(settings, 'FRONTEND_PUBLIC_URL', 'http://localhost:3000').rstrip('/')}{path}"


def issue_email_verification(user):
    raw = secrets.token_urlsafe(32)
    EmailVerificationToken.objects.filter(user=user, used_at__isnull=True).update(used_at=timezone.now())
    EmailVerificationToken.objects.create(
        user=user,
        token_hash=hashlib.sha256(raw.encode("utf-8")).hexdigest(),
        expires_at=timezone.now() + timedelta(hours=24),
    )
    send_mail(
        "Verify your QCSTS email",
        f"Open this link to verify your QCSTS email: {_frontend_url('/verify-email?token='+raw)}",
        getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@qcsts.local"),
        [user.email],
        fail_silently=False,
    )


class PasswordResetRequestView(PublicAPIView):
    """Public recovery request; it never requires tenant selection or reveals account existence."""
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = CustomUser.objects.filter(
            email__iexact=serializer.validated_data["email"], is_active=True
        ).first()
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            send_mail(
                "Reset your QCSTS password",
                f"Open this link to reset your QCSTS password: {_frontend_url('/reset-password?uid='+uid+'&token='+token)}",
                getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@qcsts.local"),
                [user.email],
                fail_silently=False,
            )
        return success_response(
            message="If an active account exists for that email, recovery instructions have been sent."
        )


class PasswordResetConfirmView(PublicAPIView):
    """Public reset completion authorized by an expiring, single-use Django reset token."""
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            uid = force_str(urlsafe_base64_decode(serializer.validated_data["uid"]))
            user = CustomUser.objects.get(pk=uid, is_active=True)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            return error_response({"detail": "Invalid or expired reset link."}, status_code=400)
        if not default_token_generator.check_token(user, serializer.validated_data["token"]):
            return error_response({"detail": "Invalid or expired reset link."}, status_code=400)
        user.set_password(serializer.validated_data["new_password"])
        user.password_changed_at = timezone.now()
        user.failed_login_attempts = 0
        user.locked_until = None
        user.save(update_fields=["password", "password_changed_at", "failed_login_attempts", "locked_until"])
        AuditService.log(performed_by=user, action="PASSWORD_RESET", model_name="CustomUser", object_id=user.id, object_repr=str(user))
        return success_response(message="Password reset successfully. You can now sign in.")


class VerifyEmailView(PublicAPIView):
    """Public email verification authorized by an expiring, hashed single-use token."""
    serializer_class = VerifyEmailSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        digest = hashlib.sha256(serializer.validated_data["token"].encode("utf-8")).hexdigest()
        record = EmailVerificationToken.objects.select_related("user").filter(
            token_hash=digest, used_at__isnull=True, expires_at__gt=timezone.now(), user__is_active=True
        ).first()
        if record is None:
            return error_response({"detail": "Invalid or expired verification link."}, status_code=400)
        now = timezone.now()
        record.used_at = now
        record.save(update_fields=["used_at"])
        record.user.email_verified_at = now
        record.user.save(update_fields=["email_verified_at"])
        AuditService.log(performed_by=record.user, action="EMAIL_VERIFIED", model_name="CustomUser", object_id=record.user.id, object_repr=str(record.user))
        return success_response(message="Email verified successfully.")