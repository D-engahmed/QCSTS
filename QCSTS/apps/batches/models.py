from django.db import models
from django.core.exceptions import ValidationError
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
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "shelf", "rack", "position"],
                condition=models.Q(is_active=True),
                name="active_chamber_location_per_org",
            )
        ]
        indexes = [
            models.Index(fields=["batch_number"]),
            models.Index(fields=["status"]),
            models.Index(fields=["study_type"]),
        ]

    def __str__(self):
        return f"{self.batch_number} ({self.product.name})"

    def save(self, *args, **kwargs):
        if self.expiry_date < self.mfg_date:
            raise ValidationError({"expiry_date": "Expiry date cannot be before the manufacturing date."})
        if self.incubation_date < self.mfg_date:
            raise ValidationError({"incubation_date": "Incubation date cannot be before the manufacturing date."})
        if self.qty_remaining > self.qty_placed:
            raise ValidationError({"qty_remaining": "Remaining quantity cannot exceed placed quantity."})
        self.assert_same_organization(product=self.product)
        super().save(*args, **kwargs)

    def get_location(self):
        return f"{self.shelf}/{self.rack}/{self.position}"

    def update_status_from_test_points(self, triggered_by=None, ip_address=None):
        """
        Update batch status based on its test points.
        Audits the transition to ensure GxP traceability.
        """
        from apps.schedule.models import TestPoint  # local import to avoid circular dependency
        from services.audit_service import AuditService

        test_points = TestPoint.objects.filter(batch=self)
        if not test_points.exists():
            return

        old_status = self.status
        
        if any(tp.status == "failed" for tp in test_points):
            new_status = "failed"
        elif all(tp.status == "completed" for tp in test_points):
            new_status = "complete"
        else:
            new_status = "active"

        if old_status != new_status:
            self.status = new_status
            self.save(update_fields=["status", "updated_at"])
            
            # Audit the automated transition
            AuditService.log(
                performed_by=triggered_by, # None for system/cron jobs
                action="UPDATE",
                model_name="Batch",
                object_id=self.id,
                object_repr=str(self),
                old_value={"status": old_status},
                new_value={"status": new_status},
                ip_address=ip_address,
                notes="Automated status transition from test point evaluation.",
                organization=self.organization,
            )