import uuid
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied


class Plan(models.Model):
    class Code(models.TextChoices):
        ESSENTIAL = "essential", "Essential"
        PROFESSIONAL = "professional", "Professional"
        ENTERPRISE = "enterprise", "Enterprise"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=32, choices=Code.choices, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    monthly_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0"))])
    annual_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0"))])
    currency = models.CharField(max_length=3, default="USD")
    max_users = models.PositiveIntegerField(null=True, blank=True)
    max_sites = models.PositiveIntegerField(null=True, blank=True)
    max_studies = models.PositiveIntegerField(null=True, blank=True)
    max_storage_mb = models.PositiveIntegerField(null=True, blank=True)
    api_access = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "billing_plan"
        ordering = ["monthly_price"]

    def __str__(self):
        return self.name


class Subscription(models.Model):
    class Status(models.TextChoices):
        TRIALING = "trialing", "Trialing"
        ACTIVE = "active", "Active"
        PAST_DUE = "past_due", "Past due"
        SUSPENDED = "suspended", "Suspended"
        CANCELED = "canceled", "Canceled"
        EXPIRED = "expired", "Expired"

    class Interval(models.TextChoices):
        MONTH = "month", "Monthly"
        YEAR = "year", "Yearly"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey("platform.Organization", on_delete=models.PROTECT, related_name="subscriptions")
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name="subscriptions")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.TRIALING)
    interval = models.CharField(max_length=8, choices=Interval.choices, default=Interval.YEAR)
    provider = models.CharField(max_length=32, default="manual")
    provider_subscription_id = models.CharField(max_length=255, blank=True)
    trial_ends_at = models.DateTimeField(null=True, blank=True)
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    cancel_at_period_end = models.BooleanField(default=False)
    canceled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "billing_subscription"
        constraints = [
            models.UniqueConstraint(
                fields=["organization"],
                condition=models.Q(status__in=["trialing", "active", "past_due"]),
                name="one_current_subscription_per_org",
            ),
        ]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["current_period_end"]),
        ]

    def __str__(self):
        return f"{self.organization} — {self.plan} ({self.status})"


class Invoice(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        OPEN = "open", "Open"
        PAID = "paid", "Paid"
        VOID = "void", "Void"
        UNCOLLECTIBLE = "uncollectible", "Uncollectible"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey("platform.Organization", on_delete=models.PROTECT, related_name="invoices")
    subscription = models.ForeignKey(Subscription, on_delete=models.PROTECT, related_name="invoices")
    number = models.CharField(max_length=64, unique=True)
    provider_order_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    provider_transaction_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    currency = models.CharField(max_length=3, default="USD")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0"))])
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"), validators=[MinValueValidator(Decimal("0"))])
    total = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0"))])
    due_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "billing_invoice"
        indexes = [models.Index(fields=["organization", "status"])]

    def __str__(self):
        return self.number

    def save(self, *args, **kwargs):
        if self.subscription_id and self.organization_id:
            if self.subscription.organization_id != self.organization_id:
                raise ValidationError(
                    {"subscription": "Invoice subscription must belong to the invoice organization."}
                )
        super().save(*args, **kwargs)


class PaymentEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey("platform.Organization", on_delete=models.PROTECT, related_name="payment_events")
    provider = models.CharField(max_length=32)
    event_id = models.CharField(max_length=255)
    event_type = models.CharField(max_length=120)
    payload = models.JSONField(default=dict)
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "billing_payment_event"
        constraints = [models.UniqueConstraint(fields=["provider", "event_id"], name="unique_billing_provider_event")]
        indexes = [models.Index(fields=["organization", "processed"])]


class UsageRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey("platform.Organization", on_delete=models.PROTECT, related_name="usage_records")
    metric = models.CharField(max_length=64)
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    quantity = models.PositiveBigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "billing_usage_record"
        constraints = [models.UniqueConstraint(fields=["organization", "metric", "period_start", "period_end"], name="unique_usage_window")]
        indexes = [models.Index(fields=["organization", "metric", "period_end"])]


class EntitlementService:
    ACTIVE_STATUSES = {Subscription.Status.TRIALING, Subscription.Status.ACTIVE, Subscription.Status.PAST_DUE}

    @classmethod
    def subscription_for(cls, organization):
        return (
            Subscription.objects.select_related("plan")
            .filter(organization=organization, status__in=cls.ACTIVE_STATUSES)
            .order_by("-created_at")
            .first()
        )

    @classmethod
    def require_usable_subscription(cls, organization):
        subscription = cls.subscription_for(organization)
        if subscription is None:
            raise PermissionDenied("The organization subscription is not active.")
        now = timezone.now()
        if subscription.trial_ends_at and subscription.status == Subscription.Status.TRIALING and subscription.trial_ends_at <= now:
            raise PermissionDenied("The organization trial has expired.")
        if subscription.current_period_end and subscription.current_period_end <= now:
            raise PermissionDenied("The organization subscription period has expired.")
        return subscription

    @classmethod
    def has_active_subscription(cls, organization):
        return cls.subscription_for(organization) is not None

    @classmethod
    def can_use_api(cls, organization):
        subscription = cls.subscription_for(organization)
        return bool(subscription and subscription.plan.api_access)

    @classmethod
    def limit_for(cls, organization, field_name):
        subscription = cls.subscription_for(organization)
        if not subscription:
            return 0
        return getattr(subscription.plan, field_name, None)
