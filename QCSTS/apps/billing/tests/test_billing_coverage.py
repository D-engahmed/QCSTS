from datetime import timedelta
from decimal import Decimal

import pytest
from django.core.management import call_command
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.accounts.tests.factories import UserFactory
from apps.billing.models import Plan, Subscription, EntitlementService
from apps.billing.services import BillingService


@pytest.mark.django_db
def test_billing_service_usage_and_idempotent_payment_event():
    user = UserFactory()
    org = user.memberships.select_related("organization").get().organization
    start = timezone.now()
    end = start + timedelta(days=30)
    record = BillingService.record_usage(organization=org, metric="users", quantity=2, period_start=start, period_end=end)
    assert record.quantity == 2
    record = BillingService.record_usage(organization=org, metric="users", quantity=3, period_start=start, period_end=end)
    assert record.quantity == 5
    with pytest.raises(ValidationError):
        BillingService.record_usage(organization=org, metric="users", quantity=-1, period_start=start, period_end=end)

    event, created = BillingService.process_payment_event(
        organization=org, provider="paymob", event_id="evt-1",
        event_type="payment.succeeded", payload={"id": 1},
    )
    assert created is True
    duplicate, created = BillingService.process_payment_event(
        organization=org, provider="paymob", event_id="evt-1",
        event_type="payment.succeeded", payload={"id": 1},
    )
    assert created is False
    assert duplicate.pk == event.pk


@pytest.mark.django_db
def test_billing_limits_active_subscription_and_cancel():
    user = UserFactory()
    org = user.memberships.select_related("organization").get().organization
    plan = Plan.objects.create(
        code="coverage-plan", name="Coverage", monthly_price=Decimal("1"),
        annual_price=Decimal("10"), max_users=2, api_access=True,
    )
    subscription = Subscription.objects.filter(organization=org).first()
    subscription.plan = plan
    subscription.status = Subscription.Status.ACTIVE
    subscription.current_period_start = timezone.now()
    subscription.current_period_end = timezone.now() + timedelta(days=30)
    subscription.save()
    assert BillingService.require_active(org) == subscription
    assert BillingService.require_limit(org, "max_users", 1) == subscription
    with pytest.raises(PermissionDenied):
        BillingService.require_limit(org, "max_users", 2)
    BillingService.cancel_at_period_end(subscription)
    subscription.refresh_from_db()
    assert subscription.cancel_at_period_end is True


@pytest.mark.django_db
def test_entitlement_expiry_and_seed_plans():
    user = UserFactory()
    org = user.memberships.select_related("organization").get().organization
    sub = Subscription.objects.filter(organization=org).first()
    sub.trial_ends_at = timezone.now() - timedelta(minutes=1)
    sub.save(update_fields=["trial_ends_at"])
    with pytest.raises(PermissionDenied):
        EntitlementService.require_usable_subscription(org)

    call_command("seed_plans")
    assert Plan.objects.filter(code__in=[
        Plan.Code.ESSENTIAL, Plan.Code.PROFESSIONAL, Plan.Code.ENTERPRISE
    ]).count() == 3
