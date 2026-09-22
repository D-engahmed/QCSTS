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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memberships")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="memberships")
    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name="memberships")
    sites = models.ManyToManyField(Site, related_name="memberships", blank=True)
    default_site = models.ForeignKey(
        Site, on_delete=models.SET_NULL, related_name="default_for_memberships", null=True, blank=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "platform_membership"
        constraints = [
            models.UniqueConstraint(fields=["user", "organization"], name="one_membership_per_org"),
            models.UniqueConstraint(
                fields=["user"],
                condition=models.Q(is_active=True),
                name="one_active_membership_per_user",
            ),
        ]
        indexes = [models.Index(fields=["user", "is_active"]), models.Index(fields=["organization", "is_active"])]

    def clean(self):
        if self.role_id and self.role.organization_id not in (None, self.organization_id):
            raise ValidationError({"role": "The role must belong to this organization or be a system role."})
        if self.default_site_id and self.default_site.organization_id != self.organization_id:
            raise ValidationError({"default_site": "The default site must belong to this organization."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def has_permission(self, code):
        return self.role.permissions.filter(code=code).exists()

    def __str__(self):
        return f"{self.user} @ {self.organization}"
