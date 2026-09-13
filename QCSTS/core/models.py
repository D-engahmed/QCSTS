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
    # Nullable only during the staged Phase 1 backfill. The follow-up migration
    # makes this mandatory after every legacy row belongs to an organization.
    organization = models.ForeignKey(
        "platform.Organization",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_records",
        db_index=True,
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

    def soft_delete(self, deleted_by=None, ip_address=None, notes=""):
        """
        Marks the record as inactive instead of deleting it.
        This is the ONLY way to 'delete' anything in QCSTS.
        
        Automatically creates an atomic AuditLog entry to ensure 
        GxP compliance and traceability.
        """
        from services.audit_service import AuditService  # Local import to avoid circular dependency
        
        old_value = {"is_active": True}
        new_value = {"is_active": False}
        
        self.is_active = False
        
        # Atomic audit log creation
        AuditService.log(
            performed_by=deleted_by,
            action="DELETE",
            model_name=self.__class__.__name__,
            object_id=self.id,
            object_repr=str(self),
            old_value=old_value,
            new_value=new_value,
            ip_address=ip_address,
            notes=notes,
            organization=self.organization if hasattr(self, "organization") else None,
        )
        
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
