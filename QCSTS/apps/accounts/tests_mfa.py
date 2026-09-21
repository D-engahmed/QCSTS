import base64
import struct
import hashlib
import hmac

from django.test import TestCase

from apps.accounts.models import CustomUser


def totp(secret, timestamp=0):
    key = base64.b32decode(secret + "=" * ((8 - len(secret) % 8) % 8))
    counter = int(timestamp // 30)
    digest = hmac.new(key, struct.pack(">Q", counter), hashlib.sha1).digest()
    index = digest[-1] & 0x0F
    binary = ((digest[index] & 0x7F) << 24) | (digest[index + 1] << 16) | (digest[index + 2] << 8) | digest[index + 3]
    return f"{binary % 1000000:06d}"


class MFATests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="mfa@acme.test",
            password="Strong-password-123",
            full_name="MFA User",
            role="analyst",
        )
        self.secret = "JBSWY3DPEHPK3PXP"
        self.user.set_mfa_secret(self.secret)
        self.user.mfa_enabled = True
        self.user.save(update_fields=["mfa_secret_encrypted", "mfa_enabled"])

    def test_totp_accepts_current_code(self):
        code = totp(self.secret)
        self.assertTrue(self.user.verify_totp(code, timestamp=0))

    def test_totp_rejects_invalid_code(self):
        self.assertFalse(self.user.verify_totp("000000", timestamp=0))

    def test_encrypted_secret_is_not_stored_as_plaintext(self):
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.mfa_secret_encrypted, self.secret)
        self.assertEqual(self.user.get_mfa_secret(), self.secret)
