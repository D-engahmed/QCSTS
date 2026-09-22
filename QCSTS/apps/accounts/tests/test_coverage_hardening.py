import hashlib
from datetime import timedelta
from unittest.mock import patch

import pytest
from django.test import RequestFactory
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import CustomUser, EmailVerificationToken
from apps.accounts.mfa import MFAConfirmView, MFADisableView, MFASetupView, MFAStatusView
from apps.accounts.recovery import (
    PasswordResetConfirmView,
    PasswordResetRequestView,
    VerifyEmailView,
    issue_email_verification,
)
from apps.accounts.views import LogoutView
from apps.accounts.tests.factories import UserFactory


@pytest.mark.django_db
def test_user_manager_and_lockout_cycle():
    with pytest.raises(ValueError):
        CustomUser.objects.create_user("")
    user = CustomUser.objects.create_user("manager@example.com", "StrongPass123!", full_name="Manager")
    assert user.email == "manager@example.com"
    user.failed_login_attempts = 4
    user.save(update_fields=["failed_login_attempts"])
    user.register_failed_login()
    assert user.is_locked_out is True
    user.reset_failed_attempts()
    assert user.failed_login_attempts == 0
    assert user.is_locked_out is False
    admin = CustomUser.objects.create_superuser("super@example.com", "StrongPass123!", full_name="Super")
    assert admin.is_superuser and admin.is_staff and admin.role == "admin"


@pytest.mark.django_db
def test_mfa_status_setup_confirm_and_disable():
    user = UserFactory()
    rf = RequestFactory()
    request = rf.get("/mfa/status/")
    request.user = user
    response = MFAStatusView.as_view()(request)
    assert response.status_code == 200

    with patch("apps.accounts.mfa.AuditService.log"), patch("apps.accounts.mfa.new_totp_secret", return_value="JBSWY3DPEHPK3PXP"):
        request = rf.post("/mfa/setup/", {}, format="json")
        request.user = user
        response = MFASetupView.as_view()(request)
    assert response.status_code == 200
    user.refresh_from_db()
    assert user.get_mfa_secret() == "JBSWY3DPEHPK3PXP"

    with patch("apps.accounts.mfa.AuditService.log"), patch.object(user, "verify_totp", return_value=False):
        request = rf.post("/mfa/confirm/", {"code": "000000"}, format="json")
        request.user = user
        response = MFAConfirmView.as_view()(request)
    assert response.status_code == 400

    with patch("apps.accounts.mfa.AuditService.log"), patch.object(user, "verify_totp", return_value=True):
        request = rf.post("/mfa/confirm/", {"code": "123456"}, format="json")
        request.user = user
        response = MFAConfirmView.as_view()(request)
    assert response.status_code == 200
    user.refresh_from_db()
    assert user.mfa_enabled is True

    with patch("apps.accounts.mfa.AuditService.log"), patch.object(user, "verify_totp", return_value=True):
        request = rf.post("/mfa/disable/", {"password": "wrong", "code": "123456"}, format="json")
        request.user = user
        response = MFADisableView.as_view()(request)
        assert response.status_code == 400
        request = rf.post("/mfa/disable/", {"password": "TestPass123!", "code": "123456"}, format="json")
        request.user = user
        response = MFADisableView.as_view()(request)
    assert response.status_code == 200
    user.refresh_from_db()
    assert user.mfa_enabled is False


@pytest.mark.django_db
def test_recovery_issue_reset_confirm_and_verify():
    user = UserFactory(email="recovery@example.com")
    with patch("apps.accounts.recovery.send_mail") as mail:
        issue_email_verification(user)
        mail.assert_called_once()
    token = EmailVerificationToken.objects.get(user=user)
    assert token.used_at is None

    rf = RequestFactory()
    with patch("apps.accounts.recovery.send_mail"):
        request = rf.post("/reset/request/", {"email": user.email}, format="json")
        response = PasswordResetRequestView.as_view()(request)
    assert response.status_code == 200

    from django.contrib.auth.tokens import default_token_generator
    from django.utils.encoding import force_bytes
    from django.utils.http import urlsafe_base64_encode

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    reset_token = default_token_generator.make_token(user)
    with patch("apps.accounts.recovery.AuditService.log"):
        request = rf.post(
            "/reset/confirm/",
            {"uid": uid, "token": reset_token, "new_password": "NewStrongPass123!"},
            format="json",
        )
        response = PasswordResetConfirmView.as_view()(request)
    assert response.status_code == 200
    user.refresh_from_db()
    assert user.check_password("NewStrongPass123!")

    raw = "email-verification-token"
    EmailVerificationToken.objects.filter(user=user).delete()
    EmailVerificationToken.objects.create(
        user=user,
        token_hash=hashlib.sha256(raw.encode()).hexdigest(),
        expires_at=timezone.now() + timedelta(hours=1),
    )
    with patch("apps.accounts.recovery.AuditService.log"):
        request = rf.post("/verify/", {"token": raw}, format="json")
        response = VerifyEmailView.as_view()(request)
    assert response.status_code == 200
    user.refresh_from_db()
    assert user.email_verified_at is not None


@pytest.mark.django_db
def test_logout_missing_invalid_and_valid_refresh():
    user = UserFactory()
    rf = RequestFactory()
    request = rf.post("/logout/", {}, format="json")
    request.user = user
    assert LogoutView.as_view()(request).status_code == 400

    request = rf.post("/logout/", {"refresh": "not-a-token"}, format="json")
    request.user = user
    assert LogoutView.as_view()(request).status_code == 400

    token = str(RefreshToken.for_user(user))
    with patch("apps.accounts.views.AuditService.log"):
        request = rf.post("/logout/", {"refresh": token}, format="json")
        request.user = user
        response = LogoutView.as_view()(request)
    assert response.status_code == 200
