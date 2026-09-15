import hashlib
import hmac
import uuid
from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import models
from core.models import BaseModel


class ElectronicSignature(BaseModel):
    class Meaning(models.TextChoices):
        REVIEW = "review", "Review"
        APPROVAL = "approval", "Approval"
        REJECTION = "rejection", "Rejection"
        RELEASE = "release", "Release"
        CLOSURE = "closure", "Closure"

    signer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="electronic_signatures")
    record_type = models.CharField(max_length=120)
    record_id = models.UUIDField()
    record_version = models.CharField(max_length=64)
    meaning = models.CharField(max_length=32, choices=Meaning.choices)
    reason = models.TextField()
    signed_at = models.DateTimeField(auto_now_add=True)
    authentication_fingerprint = models.CharField(max_length=128)
    signature_digest = models.CharField(max_length=128, unique=True)

    class Meta:
        db_table = "compliance_electronic_signature"
        ordering = ["-signed_at"]
        constraints = [models.UniqueConstraint(fields=["organization", "record_type", "record_id", "record_version", "meaning"], name="one_signature_per_record_meaning")]

    @classmethod
    def issue(cls, *, organization, signer, record_type, record_id, record_version, meaning, reason, authentication_secret):
        if not reason.strip():
            raise ValidationError("A reason is mandatory for an electronic signature.")
        if signer is None or not signer.is_active:
            raise PermissionDenied("The signer must be an active authenticated user.")
        payload = "|".join([str(organization.pk), str(signer.pk), record_type, str(record_id), record_version, meaning, reason])
        fingerprint = hmac.new(authentication_secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
        return cls.objects.create(
            organization=organization, signer=signer, record_type=record_type, record_id=record_id,
            record_version=record_version, meaning=meaning, reason=reason,
            authentication_fingerprint=fingerprint, signature_digest=hashlib.sha256(payload.encode()).hexdigest(),
        )

    def save(self, *args, **kwargs):
        if self.pk and ElectronicSignature.all_objects.filter(pk=self.pk).exists():
            raise PermissionDenied("Electronic signatures are immutable.")
        self.assert_same_organization(signer=self.signer)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise PermissionDenied("Electronic signatures cannot be deleted.")


class ValidationArtifact(BaseModel):
    class Type(models.TextChoices):
        URS = "urs", "URS"
        FRS = "frs", "FRS"
        RISK = "risk", "Risk Assessment"
        TRACEABILITY = "traceability", "Traceability Matrix"
        IQ = "iq", "IQ"
        OQ = "oq", "OQ"
        PQ = "pq", "PQ"
        SUMMARY = "summary", "Validation Summary"

    artifact_type = models.CharField(max_length=32, choices=Type.choices)
    version = models.CharField(max_length=64)
    title = models.CharField(max_length=255)
    content_hash = models.CharField(max_length=128)
    approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name="approved_validation_artifacts")
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "compliance_validation_artifact"
        constraints = [models.UniqueConstraint(fields=["organization", "artifact_type", "version"], name="validation_artifact_version_unique")]

    def save(self, *args, **kwargs):
        if self.pk and ValidationArtifact.all_objects.filter(pk=self.pk).exists():
            raise PermissionDenied("Validation artifacts are immutable after creation; create a new version.")
        if self.approved_by_id:
            self.assert_same_organization(approved_by=self.approved_by)
        super().save(*args, **kwargs)
