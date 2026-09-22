from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError
from .models import Invoice, PaymentEvent, Subscription, UsageRecord, EntitlementService


class BillingService:
    """Server-side subscription, entitlement and webhook primitives."""

    @staticmethod
    def require_active(organization):
        subscription = EntitlementService.subscription_for(organization)
        if not subscription:
            raise PermissionDenied("The organization does not have an active subscription.")
        return subscription

    @staticmethod
    def require_limit(organization, field_name, current_usage):
        subscription = BillingService.require_active(organization)
        limit = getattr(subscription.plan, field_name, None)
        if limit is not None and current_usage >= limit:
            raise PermissionDenied(f"The {field_name} entitlement has been reached.")
        return subscription

    @staticmethod
    @transaction.atomic
    def record_usage(*, organization, metric, quantity, period_start, period_end):
        if quantity < 0:
            raise ValidationError("Usage quantity cannot be negative.")
        record, _ = UsageRecord.objects.select_for_update().get_or_create(
            organization=organization, metric=metric, period_start=period_start, period_end=period_end,
            defaults={"quantity": 0},
        )
        record.quantity += quantity
        record.save(update_fields=["quantity"])
        return record

    @staticmethod
    @transaction.atomic
    def process_payment_event(*, organization, provider, event_id, event_type, payload):
        event, created = PaymentEvent.objects.select_for_update().get_or_create(
            provider=provider, event_id=event_id,
            defaults={"organization": organization, "event_type": event_type, "payload": payload},
        )
        if not created:
            if event.organization_id != organization.id:
                raise PermissionDenied(
                    "Payment event cannot be reassigned to another organization."
                )
            if event.processed:
                return event, False
        event.organization = organization
        event.event_type = event_type
        event.payload = payload
        event.processed = True
        event.processed_at = timezone.now()
        event.save(update_fields=["organization", "event_type", "payload", "processed", "processed_at"])
        return event, True

    @staticmethod
    @transaction.atomic
    def cancel_at_period_end(subscription):
        subscription.cancel_at_period_end = True
        subscription.save(update_fields=["cancel_at_period_end", "updated_at"])
        return subscription
