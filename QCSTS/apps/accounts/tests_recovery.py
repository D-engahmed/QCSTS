from django.core import mail
from django.test import TestCase

from apps.accounts.models import CustomUser, EmailVerificationToken
from apps.accounts.recovery import issue_email_verification
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken


class RecoveryFlowTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            email="recovery@acme.test",
            password="Initial-password-123",
            full_name="Recovery User",
            role="analyst",
        )

    def test_password_reset_request_is_enumeration_safe(self):
        response_existing = self.client.post(
            "/api/v1/auth/password-reset/",
            {"email": self.user.email},
            format="json",
        )
        response_unknown = self.client.post(
            "/api/v1/auth/password-reset/",
            {"email": "unknown@acme.test"},
            format="json",
        )

        self.assertEqual(response_existing.status_code, 200)
        self.assertEqual(response_unknown.status_code, 200)
        self.assertEqual(response_existing.data["message"], response_unknown.data["message"])
        self.assertEqual(len(mail.outbox), 1)

    def test_password_reset_changes_password_and_invalidates_old_password(self):
        self.client.post(
            "/api/v1/auth/password-reset/",
            {"email": self.user.email},
            format="json",
        )
        message = mail.outbox[-1].body
        import re

        match = re.search(r"reset-password\?uid=([^&]+)&token=(.+)", message)
        self.assertIsNotNone(match)
        uid, token = match.group(1), match.group(2)

        response = self.client.post(
            "/api/v1/auth/password-reset/confirm/",
            {
                "uid": uid,
                "token": token,
                "new_password": "Replacement-password-456",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("Replacement-password-456"))
        self.assertFalse(self.user.check_password("Initial-password-123"))

        reused = self.client.post(
            "/api/v1/auth/password-reset/confirm/",
            {
                "uid": uid,
                "token": token,
                "new_password": "Another-password-789",
            },
            format="json",
        )
        self.assertEqual(reused.status_code, 400)

    def test_email_verification_token_is_single_use(self):
        issue_email_verification(self.user)
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[-1].body

        import re

        match = re.search(r"verify-email\?token=(.+)", message)
        self.assertIsNotNone(match)
        token = match.group(1)

        response = self.client.post(
            "/api/v1/auth/verify-email/",
            {"token": token},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.email_verified_at)
        record = EmailVerificationToken.objects.get(user=self.user)
        self.assertIsNotNone(record.used_at)

        reused = self.client.post(
            "/api/v1/auth/verify-email/",
            {"token": token},
            format="json",
        )
        self.assertEqual(reused.status_code, 400)
