import uuid
from django.db import models
from django.conf import settings


class AuditLog(models.Model):
    """
    Immutable record of every change in the CQSTS system.

    Rules:
    - Never updated after creation
    - Never deleted
    - Created automatically by AuditService — never directly by views
    - Protected by a PostgreSQL trigger at the DB level
    """

    ACTION_CHOICES = [
        ("CREATE", "Create"),
        ("UPDATE", "Update"),
        ("DELETE", "Delete"),
        ("LOGIN", "Login"),
        ("LOGOUT", "Logout"),
        ("SIGN", "Electronic Signature"),
        ("APPROVE", "Approve"),
        ("REJECT", "Reject"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="audit_logs"
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(
        max_length=100, help_text="Name of the model that was changed. e.g. Batch, TestResult"
    )
    object_id = models.CharField(max_length=100, help_text="UUID of the record that was changed.")
    object_repr = models.CharField(
        max_length=255, help_text="Human-readable representation of the record at time of change."
    )
    old_value = models.JSONField(
        null=True, blank=True, help_text="State of the record before the change."
    )
    new_value = models.JSONField(
        null=True, blank=True, help_text="State of the record after the change."
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(
        auto_now_add=True, help_text="Exact server time when this action occurred. Never editable."
    )
    notes = models.TextField(
        blank=True, help_text="Optional context about why this change was made."
    )

    class Meta:
        db_table = "audit_log"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["model_name", "object_id"]),
            models.Index(fields=["performed_by"]),
            models.Index(fields=["timestamp"]),
        ]

    def __str__(self):
        return f"{self.action} on {self.model_name} by {self.performed_by} at {self.timestamp}"

    def save(self, *args, **kwargs):
        """
        Override save to prevent any updates.
        AuditLog records are created once and never modified.
        """
        if self.pk and AuditLog.objects.filter(pk=self.pk).exists():
            raise PermissionError("Audit log records cannot be modified.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Override delete to prevent any deletions.
        """
        raise PermissionError("Audit log records cannot be deleted.")
