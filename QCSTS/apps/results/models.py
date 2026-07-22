from django.db import models
from core.models import BaseModel, ActiveManager


class TestResult(BaseModel):
    """
    A single test result submitted by an analyst for a specific
    test point and monograph test.

    Rules:
    - Requires electronic signature (HasValidSignature permission)
    - specification_snapshot copies the spec at time of submission
    - pass_fail is calculated automatically by OutcomeEvaluator
    - Cannot be deleted or modified after submission
    - One result per (test_point, monograph_test) pair
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
        Results are immutable once saved.
        """
        if self.pk and TestResult.objects.filter(pk=self.pk).exists():
            raise PermissionError("Test results cannot be modified after submission.")
        super().save(*args, **kwargs)
