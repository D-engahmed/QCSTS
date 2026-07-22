from django.db import models
from core.models import BaseModel, ActiveManager
from constants.stability import StudyType


class Batch(BaseModel):
    """
    A manufactured batch of a product placed in the stability chamber.

    When a batch is created:
    1. ScheduleEngine automatically generates all test points
    2. Batch is saved to chamber inventory with location + qty

    Business Rules:
    - batch_number must be globally unique
    - incubation_date must be >= mfg_date
    - product must have an approved monograph
    - chamber location (shelf + rack + position) must be unique
    """

    STATUS_CHOICES = [
        ("active", "Active"),
        ("complete", "Complete"),
        ("failed", "Failed"),
        ("inactive", "Inactive"),
    ]

    product = models.ForeignKey(
        "products.Product", on_delete=models.PROTECT, related_name="batches"
    )
    batch_number = models.CharField(
        max_length=100, unique=True, help_text="e.g. AMX-2024-001. Must be globally unique."
    )
    mfg_date = models.DateField(help_text="Manufacturing date.")
    expiry_date = models.DateField(help_text="Expiry date of the batch.")
    incubation_date = models.DateField(
        help_text="Date batch was placed in stability chamber. Must be >= mfg_date."
    )
    study_type = models.CharField(
        max_length=20,
        choices=StudyType.CHOICES,
        help_text="ICH study type — determines which test points are generated.",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")

    # Chamber location
    shelf = models.CharField(max_length=50)
    rack = models.CharField(max_length=50)
    position = models.CharField(max_length=50)

    # Quantity tracking
    qty_placed = models.PositiveIntegerField(help_text="Total quantity placed in chamber.")
    qty_remaining = models.PositiveIntegerField(help_text="Quantity remaining after sample pulls.")

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        db_table = "batches_batch"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["batch_number"]),
            models.Index(fields=["status"]),
            models.Index(fields=["study_type"]),
        ]

    def __str__(self):
        return f"{self.batch_number} ({self.product.name})"

    def get_location(self):
        return f"{self.shelf}/{self.rack}/{self.position}"

    def update_status_from_test_points(self):
        """
        Update batch status based on its test points.
        Called automatically when a test point status changes.
        """
        from apps.schedule.models import TestPoint  # local import to avoid circular dependency

        test_points = TestPoint.objects.filter(batch=self)
        if not test_points.exists():
            return

        if any(tp.status == "failed" for tp in test_points):
            self.status = "failed"
        elif all(tp.status == "completed" for tp in test_points):
            self.status = "complete"
        else:
            self.status = "active"

        self.save(update_fields=["status"])