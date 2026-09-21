from django.db import models

from core.models import BaseModel, ActiveManager


class Notification(BaseModel):
    class Severity(models.TextChoices):
        INFO = "info", "Info"
        WARNING = "warning", "Warning"
        CRITICAL = "critical", "Critical"

    class Kind(models.TextChoices):
        SYSTEM = "system", "System"
        APPROVAL = "approval", "Approval"
        OVERDUE = "overdue", "Overdue"
        QUALITY = "quality", "Quality"
        BILLING = "billing", "Billing"

    user = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    kind = models.CharField(max_length=20, choices=Kind.choices, default=Kind.SYSTEM)
    severity = models.CharField(max_length=20, choices=Severity.choices, default=Severity.INFO)
    title = models.CharField(max_length=255)
    body = models.TextField()
    action_url = models.CharField(max_length=500, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        db_table = "notifications_notification"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "user", "read_at"]),
            models.Index(fields=["organization", "kind"]),
        ]

    def save(self, *args, **kwargs):
        self.assert_same_organization(user=self.user)
        super().save(*args, **kwargs)
