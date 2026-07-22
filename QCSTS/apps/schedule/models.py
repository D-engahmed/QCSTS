from django.db import models
from django.utils import timezone
from core.models import BaseModel, ActiveManager


class TestPoint(BaseModel):
    """
    A single scheduled test point for a batch.

    Rules:
    - Created ONLY by ScheduleEngine — never manually
    - No POST endpoint exists for this model
    - Status moves: pending → pulled (manual) → overdue (auto) or completed/failed
    - One TestPoint covers ALL tests defined in the monograph
    """

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("overdue", "Overdue"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("pulled", "Pulled"),  # <-- NEW STATUS ADDED
    ]

    batch = models.ForeignKey("batches.Batch", on_delete=models.CASCADE, related_name="test_points")
    month = models.PositiveIntegerField(help_text="ICH month number. e.g. 0, 3, 6, 12.")
    scheduled_date = models.DateField(help_text="Exact date this test point is due.")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    completed_at = models.DateTimeField(
        null=True, blank=True, help_text="When all results for this test point were submitted."
    )

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        db_table = "schedule_test_point"
        ordering = ["month"]
        unique_together = [["batch", "month"]]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["scheduled_date"]),
        ]

    def __str__(self):
        return f"{self.batch.batch_number} — Month {self.month} ({self.scheduled_date})"

    def is_overdue(self):
        return self.status == "pending" and self.scheduled_date < timezone.now().date()

    def update_status(self):
        """
        Update this test point's status based on its submitted results.
        Also triggers the parent batch to update its status.
        """
        from apps.results.models import TestResult  # local import to avoid circular dependency

        results = TestResult.objects.filter(test_point=self)

        if not results.exists():
            # No results yet
            if self.is_overdue() and self.status != "pulled":
                # Only mark overdue if NOT already pulled
                self.status = "overdue"
            # If it's pulled, keep it pulled. If pending/overdue, keep as is.
        elif any(r.pass_fail == "fail" for r in results):
            self.status = "failed"
        elif all(r.pass_fail == "pass" for r in results):
            self.status = "completed"
            self.completed_at = timezone.now()
        else:
            # Mixed or incomplete results (should not happen with unique_together)
            self.status = "pending"

        self.save(update_fields=["status", "completed_at"])

        # Update the parent batch status
        self.batch.update_status_from_test_points()