from django.db import models
from core.models import BaseModel, ActiveManager


class SamplePull(BaseModel):
    """
    Records every time a sample is pulled from a batch in the chamber.

    Rules:
    - qty_pulled must not exceed batch.qty_remaining
    - Every pull reduces batch.qty_remaining
    - Pulls are never deleted — soft delete only
    - Each pull is linked to a specific test point
    """

    batch = models.ForeignKey(
        "batches.Batch",
        on_delete=models.PROTECT,
        related_name="sample_pulls",
    )
    test_point = models.ForeignKey(
        "schedule.TestPoint",
        on_delete=models.PROTECT,
        related_name="sample_pulls",
        null=True,
        blank=True,
    )
    qty_pulled = models.PositiveIntegerField(help_text="Number of units pulled from chamber.")
    pulled_by = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        related_name="sample_pulls",
    )
    pulled_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        db_table = "chamber_sample_pull"
        ordering = ["-pulled_at"]

    def __str__(self):
        return f"Pull {self.qty_pulled} from {self.batch.batch_number} at {self.pulled_at}"


class LocationHistory(BaseModel):
    """
    Records every time a batch changes its chamber location.
    Step 7 from the workflow — Change + log location.
    """

    batch = models.ForeignKey(
        "batches.Batch",
        on_delete=models.PROTECT,
        related_name="location_history",
    )
    old_shelf = models.CharField(max_length=50)
    old_rack = models.CharField(max_length=50)
    old_position = models.CharField(max_length=50)
    new_shelf = models.CharField(max_length=50)
    new_rack = models.CharField(max_length=50)
    new_position = models.CharField(max_length=50)
    changed_by = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        related_name="location_changes",
    )
    reason = models.TextField(blank=True)

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        db_table = "chamber_location_history"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.batch.batch_number} moved to {self.new_shelf}/{self.new_rack}/{self.new_position}"
