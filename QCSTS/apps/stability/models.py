from django.core.exceptions import ValidationError
from django.db import models

from core.models import ActiveManager, BaseModel


class ControlledStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    APPROVED = "approved", "Approved"
    EFFECTIVE = "effective", "Effective"
    SUPERSEDED = "superseded", "Superseded"
    INACTIVE = "inactive", "Inactive"


class StorageCondition(BaseModel):
    """Controlled storage condition used by stability studies and timepoints."""

    code = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    temperature_min_c = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    temperature_max_c = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    humidity_min_rh = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    humidity_max_rh = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=ControlledStatus.choices, default=ControlledStatus.DRAFT)

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        db_table = "stability_storage_condition"
        constraints = [models.UniqueConstraint(fields=["organization", "code"], name="storage_condition_code_per_org")]
        ordering = ["code"]

    def save(self, *args, **kwargs):
        if self.temperature_min_c is not None and self.temperature_max_c is not None and self.temperature_min_c > self.temperature_max_c:
            raise ValidationError("Minimum temperature cannot exceed maximum temperature.")
        if self.humidity_min_rh is not None and self.humidity_max_rh is not None and self.humidity_min_rh > self.humidity_max_rh:
            raise ValidationError("Minimum humidity cannot exceed maximum humidity.")
        super().save(*args, **kwargs)


class Protocol(BaseModel):
    """Stable identity of a study protocol; controlled content lives in ProtocolVersion."""

    code = models.CharField(max_length=80)
    name = models.CharField(max_length=255)
    product = models.ForeignKey("products.Product", on_delete=models.PROTECT, related_name="stability_protocols")
    study_type = models.CharField(max_length=40)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=ControlledStatus.choices, default=ControlledStatus.DRAFT)

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        db_table = "stability_protocol"
        constraints = [models.UniqueConstraint(fields=["organization", "code"], name="protocol_code_per_org")]
        ordering = ["code"]

    def save(self, *args, **kwargs):
        self.assert_same_organization(product=self.product)
        super().save(*args, **kwargs)


class ProtocolVersion(BaseModel):
    """Immutable-in-practice version reference used by a StabilityStudy."""

    protocol = models.ForeignKey(Protocol, on_delete=models.PROTECT, related_name="versions")
    version = models.CharField(max_length=50)
    effective_date = models.DateField(null=True, blank=True)
    approved_by = models.ForeignKey(
        "accounts.CustomUser", on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_protocol_versions"
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    change_reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=ControlledStatus.choices, default=ControlledStatus.DRAFT)

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        db_table = "stability_protocol_version"
        constraints = [models.UniqueConstraint(fields=["protocol", "version"], name="protocol_version_unique")]
        ordering = ["protocol", "-version"]

    def save(self, *args, **kwargs):
        self.assert_same_organization(protocol=self.protocol)
        super().save(*args, **kwargs)


class Specification(BaseModel):
    """Stable identity of a product specification; approved limits live in SpecificationVersion."""

    code = models.CharField(max_length=80)
    name = models.CharField(max_length=255)
    product = models.ForeignKey("products.Product", on_delete=models.PROTECT, related_name="stability_specifications")
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=ControlledStatus.choices, default=ControlledStatus.DRAFT)

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        db_table = "stability_specification"
        constraints = [models.UniqueConstraint(fields=["organization", "code"], name="specification_code_per_org")]
        ordering = ["code"]

    def save(self, *args, **kwargs):
        self.assert_same_organization(product=self.product)
        super().save(*args, **kwargs)


class SpecificationVersion(BaseModel):
    """Versioned specification metadata. Historical study results must reference the applicable version."""

    specification = models.ForeignKey(Specification, on_delete=models.PROTECT, related_name="versions")
    version = models.CharField(max_length=50)
    effective_date = models.DateField(null=True, blank=True)
    approved_by = models.ForeignKey(
        "accounts.CustomUser", on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_specification_versions"
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    change_reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=ControlledStatus.choices, default=ControlledStatus.DRAFT)

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        db_table = "stability_specification_version"
        constraints = [models.UniqueConstraint(fields=["specification", "version"], name="specification_version_unique")]
        ordering = ["specification", "-version"]

    def save(self, *args, **kwargs):
        self.assert_same_organization(specification=self.specification)
        super().save(*args, **kwargs)


class StabilityStudy(BaseModel):
    """The central stability aggregate: one study can contain many batches and timepoints."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PLANNED = "planned", "Planned"
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        CLOSED = "closed", "Closed"
        CANCELED = "canceled", "Canceled"

    code = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    site = models.ForeignKey("platform.Site", on_delete=models.PROTECT, related_name="stability_studies")
    product = models.ForeignKey("products.Product", on_delete=models.PROTECT, related_name="stability_studies")
    protocol_version = models.ForeignKey(ProtocolVersion, on_delete=models.PROTECT, related_name="studies")
    study_type = models.CharField(max_length=40)
    start_date = models.DateField(null=True, blank=True)
    target_end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    objective = models.TextField(blank=True)

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        db_table = "stability_study"
        constraints = [models.UniqueConstraint(fields=["organization", "code"], name="study_code_per_org")]
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        self.assert_same_organization(site=self.site, product=self.product, protocol_version=self.protocol_version)
        if self.site.organization_id != self.organization_id:
            raise ValidationError({"site": "The study site must belong to the study organization."})
        if self.protocol_version.protocol.product_id != self.product_id:
            raise ValidationError({"protocol_version": "The protocol version must belong to the study product."})
        super().save(*args, **kwargs)


class StudyBatch(BaseModel):
    """Enrollment of a manufactured batch into a specific stability study."""

    study = models.ForeignKey(StabilityStudy, on_delete=models.PROTECT, related_name="study_batches")
    batch = models.ForeignKey("batches.Batch", on_delete=models.PROTECT, related_name="stability_enrollments")
    enrolled_at = models.DateTimeField(null=True, blank=True)
    planned_quantity = models.PositiveIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        db_table = "stability_study_batch"
        constraints = [models.UniqueConstraint(fields=["study", "batch"], name="study_batch_unique")]

    def save(self, *args, **kwargs):
        self.assert_same_organization(study=self.study, batch=self.batch)
        if self.batch.product_id != self.study.product_id:
            raise ValidationError({"batch": "The enrolled batch must belong to the study product."})
        super().save(*args, **kwargs)


class StudyTimepoint(BaseModel):
    """Controlled timepoint definition attached to a study, not to a mutable global schedule."""

    class Status(models.TextChoices):
        PLANNED = "planned", "Planned"
        OPEN = "open", "Open"
        COMPLETED = "completed", "Completed"
        CANCELED = "canceled", "Canceled"

    study = models.ForeignKey(StabilityStudy, on_delete=models.PROTECT, related_name="timepoints")
    code = models.CharField(max_length=50)
    nominal_days = models.PositiveIntegerField()
    target_date = models.DateField()
    tolerance_days = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLANNED)

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        db_table = "stability_study_timepoint"
        constraints = [models.UniqueConstraint(fields=["study", "code"], name="study_timepoint_code_unique")]
        ordering = ["nominal_days", "code"]

    def save(self, *args, **kwargs):
        self.assert_same_organization(study=self.study)
        super().save(*args, **kwargs)


class StabilitySample(BaseModel):
    """Traceable sample identity linking study, batch, timepoint and storage condition."""

    class Status(models.TextChoices):
        STORED = "stored", "Stored"
        PULLED = "pulled", "Pulled"
        TESTING = "testing", "Testing"
        COMPLETED = "completed", "Completed"
        DISPOSED = "disposed", "Disposed"
        RETAINED = "retained", "Retained"

    sample_code = models.CharField(max_length=120)
    study = models.ForeignKey(StabilityStudy, on_delete=models.PROTECT, related_name="samples")
    study_batch = models.ForeignKey(StudyBatch, on_delete=models.PROTECT, related_name="samples")
    timepoint = models.ForeignKey(StudyTimepoint, on_delete=models.PROTECT, related_name="samples")
    storage_condition = models.ForeignKey(StorageCondition, on_delete=models.PROTECT, related_name="samples")
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.STORED)
    chamber_reference = models.CharField(max_length=120, blank=True)
    location_reference = models.CharField(max_length=120, blank=True)

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        db_table = "stability_sample"
        constraints = [models.UniqueConstraint(fields=["organization", "sample_code"], name="sample_code_per_org")]
        ordering = ["sample_code"]

    def save(self, *args, **kwargs):
        self.assert_same_organization(
            study=self.study,
            study_batch=self.study_batch,
            timepoint=self.timepoint,
            storage_condition=self.storage_condition,
        )
        if self.study_batch.study_id != self.study_id or self.timepoint.study_id != self.study_id:
            raise ValidationError("Sample study, batch enrollment and timepoint must refer to the same study.")
        super().save(*args, **kwargs)
