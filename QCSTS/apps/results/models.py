from django.db import models
from core.models import BaseModel, ActiveManager

class TestResult(BaseModel):
    """
    A single test result submitted by an analyst for a specific
    test point and monograph test.
    """

    PASS_FAIL_CHOICES = [
        ("pass", "Pass"),
        ("fail", "Fail"),
        ("pending", "Pending"),
    ]

    test_point = models.ForeignKey(
        "schedule.TestPoint",
        on_delete=models.PROTECT,
        related_name="results",
    )
    monograph_test = models.ForeignKey(
        "products.MonographTest",
        on_delete=models.PROTECT,
        related_name="results",
    )
    value = models.CharField(
        max_length=255,
        help_text="The measured value e.g. 99.5, 6.8, 74%",
    )
    unit = models.CharField(
        max_length=50,
        blank=True,
        help_text="Unit of measurement e.g. %, mg, pH units",
    )
    specification_snapshot = models.CharField(
        max_length=500,
        help_text="Copy of the spec at time of submission. Immutable after save.",
    )
    pass_fail = models.CharField(
        max_length=10,
        choices=PASS_FAIL_CHOICES,
        default="pending",
    )
    analyst = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        related_name="submitted_results",
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        db_table = "results_test_result"
        ordering = ["-submitted_at"]
        unique_together = [["test_point", "monograph_test"]]
        indexes = [
            models.Index(fields=["pass_fail"]),
            models.Index(fields=["submitted_at"]),
        ]

    def __str__(self):
        return f"{self.monograph_test.name} — {self.value} ({self.pass_fail})"

    def save(self, *args, **kwargs):
        """
        Prevent modification after initial submission.
        """
        update_fields = kwargs.get("update_fields")
        
        if update_fields and set(update_fields) == {"is_active", "updated_at"}:
            super().save(*args, **kwargs)
            return

        if self.pk and TestResult.all_objects.filter(pk=self.pk).exists():
            raise PermissionError("Test results cannot be modified after submission.")
            
        if self.organization_id is None and self.test_point_id:
            self.organization = self.test_point.batch.organization
            
        super().save(*args, **kwargs)

    def workflow_state(self):
        """
        Derive workflow state from immutable ResultReview records.
        """
        reviews = self.reviews.all()

        if reviews.filter(action="QA_APPROVE").exists():
            return "approved"

        if reviews.filter(action="QA_REJECT").exists():
            return "rejected"

        if reviews.filter(action="SUPERVISOR_REVIEW").exists():
            return "under_review"

        return "submitted"

    def build_review_snapshot(self):
        """
        Captures the exact submitted result version reviewed/signed.
        """
        return {
            "result_id": str(self.id),
            "test_point_id": str(self.test_point_id),
            "monograph_test_id": str(self.monograph_test_id),
            "value": self.value,
            "unit": self.unit,
            "specification_snapshot": self.specification_snapshot,
            "pass_fail": self.pass_fail,
            "analyst_id": str(self.analyst_id) if self.analyst_id else None,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
        }


class ResultReview(BaseModel):
    """
    Immutable workflow decision for a submitted TestResult.
    """

    ACTION_CHOICES = [
        ("SUPERVISOR_REVIEW", "Supervisor Review"),
        ("QA_APPROVE", "QA Approve"),
        ("QA_REJECT", "QA Reject"),
    ]

    result = models.ForeignKey(
        "results.TestResult",
        on_delete=models.PROTECT,
        related_name="reviews",
    )

    action = models.CharField(
        max_length=30,
        choices=ACTION_CHOICES,
    )

    reviewed_by = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        related_name="result_reviews",
    )

    comments = models.TextField(blank=True)

    result_snapshot = models.JSONField(
        help_text="Immutable snapshot of the result at the time of review decision."
    )

    reviewed_at = models.DateTimeField(auto_now_add=True)

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        db_table = "results_result_review"
        ordering = ["-reviewed_at"]
        indexes = [
            models.Index(fields=["action"]),
            models.Index(fields=["reviewed_at"]),
            models.Index(fields=["result", "action"]),
        ]

    def __str__(self):
        return f"{self.action} for {self.result_id} by {self.reviewed_by}"

    def save(self, *args, **kwargs):
        """
        Review records are immutable once created.
        """
        update_fields = kwargs.get("update_fields")
        
        if update_fields and set(update_fields) == {"is_active", "updated_at"}:
            super().save(*args, **kwargs)
            return

        if self.pk and ResultReview.all_objects.filter(pk=self.pk).exists():
            raise PermissionError("Result review records cannot be modified.")
        if self.organization_id is None and self.result_id:
            self.organization = self.result.organization
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise PermissionError("Result review records cannot be deleted.")