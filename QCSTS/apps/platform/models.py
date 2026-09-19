import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Organization(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        SUSPENDED = "suspended", "Suspended"
        ARCHIVED = "archived", "Archived"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    legal_name = models.CharField(max_length=255, blank=True)
    slug = models.SlugField(max_length=80, unique=True)
    country = models.CharField(max_length=2)
    timezone = models.CharField(max_length=64, default="UTC")
    currency = models.CharField(max_length=3, default="USD")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "platform_organization"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Site(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, related_name="sites")
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    country = models.CharField(max_length=2)
    timezone = models.CharField(max_length=64, default="UTC")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "platform_site"
        constraints = [models.UniqueConstraint(fields=["organization", "name"], name="site_name_per_org")]
        ordering = ["organization__name", "name"]

    def __str__(self):
        return f"{self.organization}: {self.name}"


class Permission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.SlugField(max_length=100, unique=True)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "platform_permission"
        ordering = ["code"]

    def __str__(self):
        return self.code


class Role(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="roles", null=True, blank=True
    )
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField(Permission, related_name="roles", blank=True)
    is_system = models.BooleanField(default=False)
    scope = models.CharField(
        max_length=20,
        choices=[("SITE", "Site"), ("ORGANIZATION", "Organization")],
        default="SITE",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "platform_role"
        constraints = [
            models.UniqueConstraint(fields=["organization", "name"], name="role_name_per_org"),
        ]
        ordering = ["name"]

    def __str__(self):
        return self.name


class Membership(models.Model):
    """Exactly one customer authorization context for an identity."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="membership",
    )
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="memberships"
    )
    site = models.ForeignKey(
        Site, on_delete=models.PROTECT, related_name="memberships"
    )
    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name="memberships")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "platform_membership"
        constraints = [
            models.UniqueConstraint(fields=["user"], name="one_membership_per_user"),
        ]
        indexes = [
            models.Index(fields=["user", "is_active"]),
            models.Index(fields=["organization", "is_active"]),
            models.Index(fields=["site", "is_active"]),
        ]

    def clean(self):
        if self.site_id and self.site.organization_id != self.organization_id:
            raise ValidationError({"site": "The site must belong to the membership organization."})
        if self.role_id and self.role.organization_id not in (None, self.organization_id):
            raise ValidationError({"role": "The role must belong to this organization or be a system role."})
        if self.role_id and self.role.scope == "ORGANIZATION":
            return

    def has_permission(self, code):
        return self.role.permissions.filter(code=code).exists()

    def __str__(self):
        return f"{self.user} @ {self.organization} / {self.site}"
