import uuid
from django.db import models
from django.conf import settings


class BaseModel(models.Model):
    """
    Abstract base model inherited by every model in QCSTS.

    Provides:
        id          — UUID primary key (not sequential integer)
        created_at  — when the record was created (server time, auto)
        updated_at  — when the record was last modified (server time, auto)
        created_by  — which user created this record
        is_active   — soft delete flag (False = deleted, record preserved)

    Why UUID instead of integer ID?
        Sequential IDs (1, 2, 3...) expose information:
        - How many records exist
        - Allows enumeration attacks (/api/batches/1, /api/batches/2...)
        UUIDs are random and reveal nothing.

    Why is_active instead of DELETE?
        GxP compliance requires all records to be preserved forever.
        Hard deleting a batch or test result is a compliance violation.
        We set is_active=False and filter it out in queries.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for this record. Auto-generated UUID.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when this record was created. Set by server, never editable.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp of last modification. Updated automatically on every save.",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_created",
        help_text="The user who created this record.",
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Soft delete flag. False means logically deleted. Record is never hard-deleted.",
    )

    class Meta:
        abstract = True  # Django will NOT create a table for BaseModel itself
        ordering = ["-created_at"]  # newest first by default

    def soft_delete(self, deleted_by=None):
        """
        Marks the record as inactive instead of deleting it.
        This is the ONLY way to 'delete' anything in QCSTS.

        The caller (service layer) is responsible for writing
        the AuditLog entry before calling this method.
        """
        self.is_active = False
        # TODO : AuditService.log() call to be added when audit app is built
        self.save(update_fields=["is_active", "updated_at"])

    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.id}>"


class ActiveManager(models.Manager):
    """
    Custom manager that automatically filters out soft-deleted records.

    Usage on a model:
        objects = ActiveManager()

    Then:
        Batch.objects.all()         ← only active batches
        Batch.all_objects.all()     ← all batches including deleted

    Every model that inherits BaseModel should add:
        objects = ActiveManager()
        all_objects = models.Manager()
    """

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)
