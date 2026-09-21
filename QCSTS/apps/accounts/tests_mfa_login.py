import base64
import hashlib
import hmac
import struct
import time

from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import CustomUser


def code_for(secret):
    key = base64.b32decode(secret + "=" * ((8 - len(secret) % 8) % 8))
    counter = int(time.time() // 30)
    digest = hmac.new(key, struct.pack(">Q", counter), hashlib.sha1).digest()
    index = digest[-1] & 0x0F
    binary = ((digest[index] & 0x7F) << 24) | (digest[index + 1] << 16) | (digest[index + 2] << 8) | digest[index + 3]
    return f"{binary % 1000000:06d}"


class MFALoginTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            email="mfa-login@acme.test",
            password="Strong-password-123",
            full_name="MFA Login User",
            role="analyst",
        )
        secret = "JBSWY3DPEHPK3PXP"
        self.user.set_mfa_secret(secret)
        self.user.mfa_enabled = True
        self.user.save(update_fields=["mfa_secret_encrypted", "mfa_enabled"])

    def test_mfa_login_requires_otp(self):
        response = self.client.post(
            "/api/v1/auth/login/",
            {"email": self.user.email, "password": "Strong-password-123"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("otp", response.data["errors"])

    def test_mfa_login_accepts_valid_otp(self):
        response = self.client.post(
            "/api/v1/auth/login/",
            {
                "email": self.user.email,
                "password": "Strong-password-123",
                "otp": code_for("JBSWY3DPEHPK3PXP"),
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["data"]["user"]["email_verified_at"] is None)
