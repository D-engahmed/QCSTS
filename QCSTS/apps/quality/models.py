from django.db import models
from core.models import BaseModel, ActiveManager


class QualityEvent(BaseModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        INVESTIGATION = "investigation", "Investigation"
        PENDING_APPROVAL = "pending_approval", "Pending approval"
        APPROVED = "approved", "Approved"
        CLOSED = "closed", "Closed"
        CANCELED = "canceled", "Canceled"

    class Severity(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    reference = models.CharField(max_length=64)
    title = models.CharField(max_length=255)
    description = models.TextField()
    severity = models.CharField(max_length=16, choices=Severity.choices, default=Severity.MEDIUM)
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.OPEN)
    # This model is abstract. Django expands %(class)s for each concrete model,
    # preventing reverse-accessor collisions between OOS/OOT/Deviation/CAPA/etc.
    owner = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_quality_events_owned",
    )
    due_at = models.DateTimeField(null=True, blank=True)
    root_cause = models.TextField(blank=True)
    impact_assessment = models.TextField(blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if self.owner_id:
            self.assert_same_organization(owner=self.owner)
        super().save(*args, **kwargs)


class OOSInvestigation(QualityEvent):
    result = models.ForeignKey("results.TestResult", on_delete=models.PROTECT, related_name="oos_investigations")
    phase = models.CharField(max_length=32, default="phase_i")
    laboratory_assessment = models.TextField(blank=True)
    manufacturing_assessment = models.TextField(blank=True)
    disposition = models.TextField(blank=True)
    class Meta:
        db_table = "quality_oos_investigation"
        constraints = [models.UniqueConstraint(fields=["organization", "reference"], name="oos_reference_per_org")]
    def save(self, *args, **kwargs):
        self.assert_same_organization(result=self.result)
        super().save(*args, **kwargs)


class OOTInvestigation(QualityEvent):
    result = models.ForeignKey("results.TestResult", on_delete=models.PROTECT, related_name="oot_investigations")
    trend_description = models.TextField(blank=True)
    statistical_assessment = models.TextField(blank=True)
    disposition = models.TextField(blank=True)
    class Meta:
        db_table = "quality_oot_investigation"
        constraints = [models.UniqueConstraint(fields=["organization", "reference"], name="oot_reference_per_org")]
    def save(self, *args, **kwargs):
        self.assert_same_organization(result=self.result)
        super().save(*args, **kwargs)


class Deviation(QualityEvent):
    detected_at = models.DateTimeField(null=True, blank=True)
    process_area = models.CharField(max_length=120, blank=True)
    immediate_action = models.TextField(blank=True)
    risk_score = models.PositiveIntegerField(null=True, blank=True)
    class Meta:
        db_table = "quality_deviation"
        constraints = [models.UniqueConstraint(fields=["organization", "reference"], name="deviation_reference_per_org")]


class CAPA(QualityEvent):
    corrective_action = models.TextField()
    preventive_action = models.TextField(blank=True)
    effectiveness_check = models.TextField(blank=True)
    effectiveness_due_at = models.DateTimeField(null=True, blank=True)
    effectiveness_verified_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = "quality_capa"
        constraints = [models.UniqueConstraint(fields=["organization", "reference"], name="capa_reference_per_org")]


class ChangeControl(QualityEvent):
    change_type = models.CharField(max_length=120)
    current_state = models.TextField()
    proposed_state = models.TextField()
    risk_assessment = models.TextField()
    implementation_plan = models.TextField(blank=True)
    implemented_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = "quality_change_control"
        constraints = [models.UniqueConstraint(fields=["organization", "reference"], name="change_reference_per_org")]
