import uuid
from datetime import timedelta

from django.db import models
from django.utils import timezone
import base64
import hashlib
import hmac
import struct
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from cryptography.fernet import Fernet

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("role", "admin")
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("qa_manager", "QA Manager"),
        ("supervisor", "Supervisor"),
        ("analyst", "Analyst"),
        ("system", "System"),   # New System Role
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="analyst") # Fixed String
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    failed_login_attempts = models.IntegerField(default=0)
    locked_until = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Set by repeated failed logins. Expires on its own — see LOCKOUT_MINUTES.",
    )
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    password_changed_at = models.DateTimeField(null=True, blank=True)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    mfa_enabled = models.BooleanField(default=False)
    mfa_secret_encrypted = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    objects = CustomUserManager()

    class Meta:
        db_table = "accounts_user"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} ({self.email})"

    # Repeated failures lock the account for a WINDOW. They must not set
    # is_active=False: that flag is the soft-delete marker, so a permanent
    # lockout made a locked account indistinguishable from a deleted one and
    # handed anyone who knew an email address a free, irreversible denial of
    # service. A self-expiring window stops brute force without that.
    LOCKOUT_THRESHOLD = 5
    LOCKOUT_MINUTES = 15

    @property
    def is_locked_out(self):
        return bool(self.locked_until and self.locked_until > timezone.now())

    def register_failed_login(self):
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= self.LOCKOUT_THRESHOLD:
            self.locked_until = timezone.now() + timedelta(minutes=self.LOCKOUT_MINUTES)
        self.save(update_fields=["failed_login_attempts", "locked_until"])

    def reset_failed_attempts(self):
        self.failed_login_attempts = 0
        self.locked_until = None
        self.save(update_fields=["failed_login_attempts", "locked_until"])


class EmailVerificationToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="email_verification_tokens")
    token_hash = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "accounts_email_verification_token"
        indexes = [
            models.Index(fields=["user", "expires_at"]),
        ]

    def set_mfa_secret(self, secret):
        key = getattr(settings, "MFA_ENCRYPTION_KEY", "")
        if not key:
            raise RuntimeError("MFA_ENCRYPTION_KEY is not configured.")
        self.mfa_secret_encrypted = Fernet(key.encode()).encrypt(secret.encode()).decode()

    def get_mfa_secret(self):
        key = getattr(settings, "MFA_ENCRYPTION_KEY", "")
        if not key or not self.mfa_secret_encrypted:
            return None
        return Fernet(key.encode()).decrypt(self.mfa_secret_encrypted.encode()).decode()

    def verify_totp(self, code, timestamp=None):
        secret = self.get_mfa_secret()
        if not secret or not code or not code.isdigit() or len(code) != 6:
            return False
        timestamp = timezone.now().timestamp() if timestamp is None else timestamp
        counter = int(timestamp // 30)
        padding = "=" * ((8 - len(secret) % 8) % 8)
        key = base64.b32decode(secret.upper() + padding)
        for offset in (-1, 0, 1):
            moving = counter + offset
            digest = hmac.new(key, struct.pack(">Q", moving), hashlib.sha1).digest()
            index = digest[-1] & 0x0F
            binary = ((digest[index] & 0x7F) << 24) | (digest[index + 1] << 16) | (digest[index + 2] << 8) | digest[index + 3]
            expected = f"{binary % 1000000:06d}"
            if hmac.compare_digest(expected, code):
                return True
        return False
