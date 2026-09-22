import base64
import hashlib
import hmac
import struct
import time
from decimal import Decimal
from datetime import timedelta

import pytest
from django.core import mail
from django.core.management import call_command
from django.utils import timezone
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.test import APIClient

from apps.accounts.tests.factories import AdminFactory, QAManagerFactory, UserFactory
from apps.billing.models import Plan, Subscription, UsageRecord, PaymentEvent
from apps.billing.services import BillingService
from apps.notifications.models import Notification
from apps.notifications.services import create_notification
from apps.quality.models import Deviation
from apps.schedule.tests.factories import TestPointFactory
from apps.batches.models import Batch
from apps.products.tests.factories import ProductFactory
from apps.platform.models import Organization
from apps.stability.api import StabilityTenantViewSet
from apps.stability.models import (
    ProtocolVersion,
    SpecificationVersion,
    StabilityStudy,
    StudyTimepoint,
    StabilitySample,
    StorageCondition,
    Protocol,
)
from apps.notifications.tasks import notify_upcoming_and_overdue_test_points
from apps.quality.views import QualityTenantViewSet
from core.permissions import IsAnalystOrAbove
from core.views import TenantScopedAPIView, TenantScopedViewSet, TenantScopedModelViewSet


def _totp(secret, timestamp=None):
    timestamp = time.time() if timestamp is None else timestamp
    key = base64.b32decode(secret + "=" * ((8 - len(secret) % 8) % 8))
    counter = int(timestamp // 30)
    digest = hmac.new(key, struct.pack(">Q", counter), hashlib.sha1).digest()
    index = digest[-1] & 0x0F
    binary = (
        ((digest[index] & 0x7F) << 24)
        | (digest[index + 1] << 16)
        | (digest[index + 2] << 8)
        | digest[index + 3]
    )
    return f"{binary % 1000000:06d}"


@pytest.mark.django_db
class TestMFAViews:
    def test_status_reports_disabled(self):
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get("/api/v1/auth/mfa/status/")
        assert response.status_code == 200
        assert response.data["data"]["enabled"] is False

    def test_setup_returns_secret_and_uri(self):
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post("/api/v1/auth/mfa/setup/")
        assert response.status_code == 200
        secret = response.data["data"]["secret"]
        assert len(secret) == 32
        assert response.data["data"]["otpauth_uri"].startswith("otpauth://totp/")
        user.refresh_from_db()
        assert user.get_mfa_secret() == secret

    def test_setup_rejects_already_enabled_mfa(self):
        user = UserFactory()
        user.mfa_enabled = True
        user.save(update_fields=["mfa_enabled"])
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post("/api/v1/auth/mfa/setup/")
        assert response.status_code == 400

    def test_confirm_enables_mfa_with_valid_code(self):
        user = UserFactory()
        secret = "JBSWY3DPEHPK3PXP"
        user.set_mfa_secret(secret)
        user.save(update_fields=["mfa_secret_encrypted"])
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post("/api/v1/auth/mfa/confirm/", {"code": _totp(secret)})
        assert response.status_code == 200
        user.refresh_from_db()
        assert user.mfa_enabled is True

    def test_confirm_rejects_invalid_code(self):
        user = UserFactory()
        secret = "JBSWY3DPEHPK3PXP"
        user.set_mfa_secret(secret)
        user.save(update_fields=["mfa_secret_encrypted"])
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post("/api/v1/auth/mfa/confirm/", {"code": "000000"})
        assert response.status_code == 400

    def test_confirm_rejects_when_already_enabled(self):
        user = UserFactory()
        user.mfa_enabled = True
        user.save(update_fields=["mfa_enabled"])
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post("/api/v1/auth/mfa/confirm/", {"code": "000000"})
        assert response.status_code == 400

    def test_disable_requires_password_and_valid_code(self):
        user = UserFactory()
        secret = "JBSWY3DPEHPK3PXP"
        user.set_mfa_secret(secret)
        user.mfa_enabled = True
        user.save(update_fields=["mfa_secret_encrypted", "mfa_enabled"])
        client = APIClient()
        client.force_authenticate(user=user)

        bad_password = client.post(
            "/api/v1/auth/mfa/disable/",
            {"password": "wrong-password", "code": _totp(secret)},
        )
        assert bad_password.status_code == 400

        invalid_code = client.post(
            "/api/v1/auth/mfa/disable/",
            {"password": "TestPass123!", "code": "000000"},
        )
        assert invalid_code.status_code == 400

        success = client.post(
            "/api/v1/auth/mfa/disable/",
            {"password": "TestPass123!", "code": _totp(secret)},
        )
        assert success.status_code == 200
        user.refresh_from_db()
        assert user.mfa_enabled is False
        assert user.get_mfa_secret() is None

    def test_disable_rejects_when_mfa_is_not_enabled(self):
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post(
            "/api/v1/auth/mfa/disable/",
            {"password": "TestPass123!", "code": "000000"},
        )
        assert response.status_code == 400


@pytest.mark.django_db
class TestBillingService:
    def test_require_active_returns_current_subscription(self):
        user = UserFactory()
        organization = user.memberships.select_related("organization").get().organization
        subscription = BillingService.require_active(organization)
        assert subscription.organization_id == organization.id

    def test_require_active_rejects_without_subscription(self):
        organization = Organization.objects.create(
            name="No Billing", slug="no-billing-service", country="EG"
        )
        with pytest.raises(Exception, match="active subscription"):
            BillingService.require_active(organization)

    def test_require_limit_allows_and_rejects_at_limit(self):
        user = UserFactory()
        organization = user.memberships.select_related("organization").get().organization
        subscription = BillingService.require_active(organization)
        assert BillingService.require_limit(organization, "max_users", 0) == subscription
        with pytest.raises(Exception, match="entitlement"):
            BillingService.require_limit(organization, "max_users", subscription.plan.max_users)

    def test_record_usage_accumulates_and_rejects_negative(self):
        user = UserFactory()
        organization = user.memberships.select_related("organization").get().organization
        start = timezone.now()
        end = start + timedelta(days=30)
        first = BillingService.record_usage(
            organization=organization,
            metric="storage_mb",
            quantity=5,
            period_start=start,
            period_end=end,
        )
        second = BillingService.record_usage(
            organization=organization,
            metric="storage_mb",
            quantity=7,
            period_start=start,
            period_end=end,
        )
        assert first.id == second.id
        assert second.quantity == 12
        assert UsageRecord.objects.get(pk=first.pk).quantity == 12
        with pytest.raises(Exception, match="negative"):
            BillingService.record_usage(
                organization=organization,
                metric="storage_mb",
                quantity=-1,
                period_start=start,
                period_end=end,
            )

    def test_payment_event_is_idempotent(self):
        user = UserFactory()
        organization = user.memberships.select_related("organization").get().organization
        first, created = BillingService.process_payment_event(
            organization=organization,
            provider="paymob",
            event_id="evt-001",
            event_type="transaction.success",
            payload={"amount": "399.00"},
        )
        assert created is True
        assert first.processed is True
        second, created_again = BillingService.process_payment_event(
            organization=organization,
            provider="paymob",
            event_id="evt-001",
            event_type="transaction.success",
            payload={"amount": "399.00"},
        )
        assert second.id == first.id
        assert created_again is False
        assert PaymentEvent.objects.count() == 1

    def test_cancel_at_period_end_sets_flag(self):
        user = UserFactory()
        organization = user.memberships.select_related("organization").get().organization
        subscription = Subscription.objects.get(organization=organization)
        assert subscription.cancel_at_period_end is False
        BillingService.cancel_at_period_end(subscription)
        subscription.refresh_from_db()
        assert subscription.cancel_at_period_end is True


@pytest.mark.django_db
class TestQualityTransitions:
    def _event(self, user, status="open"):
        organization = user.memberships.select_related("organization").get().organization
        return Deviation.objects.create(
            organization=organization,
            created_by=user,
            owner=user,
            reference=f"DEV-{str(time.time_ns())[-8:]}",
            title="Temperature excursion",
            description="Chamber temperature exceeded limit.",
            status=status,
        )

    def test_invalid_transition_returns_400(self):
        user = AdminFactory()
        event = self._event(user, status="open")
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post(
            f"/api/v1/quality/deviations/{event.id}/transition/",
            {"status": "approved", "comments": "Invalid direct approval."},
            format="json",
        )
        assert response.status_code == 400

    def test_cancel_requires_comments(self):
        user = AdminFactory()
        event = self._event(user)
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post(
            f"/api/v1/quality/deviations/{event.id}/transition/",
            {"status": "canceled"},
            format="json",
        )
        assert response.status_code == 400

    def test_investigation_transition_succeeds(self):
        user = AdminFactory()
        event = self._event(user)
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post(
            f"/api/v1/quality/deviations/{event.id}/transition/",
            {"status": "investigation", "comments": "Initial investigation started."},
            format="json",
        )
        assert response.status_code == 200
        event.refresh_from_db()
        assert event.status == "investigation"

    def test_approval_requires_signature(self):
        qa = QAManagerFactory()
        event = self._event(qa, status="pending_approval")
        client = APIClient()
        client.force_authenticate(user=qa)
        response = client.post(
            f"/api/v1/quality/deviations/{event.id}/transition/",
            {"status": "approved", "comments": "QA approval."},
            format="json",
        )
        assert response.status_code == 403

    def test_approval_with_signature_succeeds(self):
        qa = QAManagerFactory()
        event = self._event(qa, status="pending_approval")
        from services.signature_service import SignatureService

        token = SignatureService.issue(qa)
        client = APIClient()
        client.force_authenticate(user=qa)
        response = client.post(
            f"/api/v1/quality/deviations/{event.id}/transition/",
            {"status": "approved", "comments": "QA approval after review."},
            format="json",
            HTTP_X_SIGNATURE_TOKEN=token,
        )
        assert response.status_code == 200
        event.refresh_from_db()
        assert event.status == "approved"

    def test_close_with_signature_sets_closed_at(self):
        qa = QAManagerFactory()
        event = self._event(qa, status="approved")
        from services.signature_service import SignatureService

        token = SignatureService.issue(qa)
        client = APIClient()
        client.force_authenticate(user=qa)
        response = client.post(
            f"/api/v1/quality/deviations/{event.id}/transition/",
            {"status": "closed", "comments": "Investigation closed."},
            format="json",
            HTTP_X_SIGNATURE_TOKEN=token,
        )
        assert response.status_code == 200
        event.refresh_from_db()
        assert event.status == "closed"
        assert event.closed_at is not None


@pytest.mark.django_db
class TestReporting:
    def test_analytics_handles_empty_tenant(self):
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get("/api/v1/reports/analytics/")
        assert response.status_code == 200
        assert response.data["data"]["results"] == []
        assert response.data["data"]["batches"] == []
        assert response.data["data"]["test_points"] == []
        assert response.data["data"]["quality"] == []

    @pytest.mark.parametrize("resource", ["results", "batches", "test-points", "quality"])
    def test_csv_export_supports_each_resource(self, resource):
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get(f"/api/v1/reports/export.csv?resource={resource}")
        assert response.status_code == 200
        assert response["Content-Type"].startswith("text/csv")
        assert "qcsts-" + resource in response["Content-Disposition"]

    def test_csv_export_rejects_unknown_resource(self):
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get("/api/v1/reports/export.csv?resource=unknown")
        assert response.status_code == 400
        assert "Unsupported resource" in response.data["detail"]


@pytest.mark.django_db
class TestNotifications:
    def test_create_notification_without_email(self):
        user = UserFactory()
        organization = user.memberships.select_related("organization").get().organization
        record = create_notification(
            user=user,
            organization=organization,
            title="No email",
            body="Body",
            send_email=False,
        )
        assert record.pk is not None
        assert mail.outbox == []

    def test_create_notification_sends_email_when_enabled(self):
        user = UserFactory()
        organization = user.memberships.select_related("organization").get().organization
        create_notification(
            user=user,
            organization=organization,
            title="Test notification",
            body="Body",
            send_email=True,
        )
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == [user.email]


@pytest.mark.django_db
def test_seed_plans_command_is_idempotent():
    call_command("seed_plans")
    assert Plan.objects.count() == 3
    professional = Plan.objects.get(code=Plan.Code.PROFESSIONAL)
    assert professional.monthly_price == Decimal("899.00")
    call_command("seed_plans")
    assert Plan.objects.count() == 3


def test_tenant_base_view_permission_guards_are_fail_closed():
    class GoodView(TenantScopedAPIView):
        permission_classes = [IsAnalystOrAbove]

    class NoDeclaration(TenantScopedAPIView):
        pass

    class BadPublic(TenantScopedAPIView):
        permission_classes = [AllowAny]

    class AuthOnly(TenantScopedAPIView):
        permission_classes = [IsAuthenticated]

    assert len(GoodView().get_permissions()) == 1
    with pytest.raises(RuntimeError, match="explicitly declare"):
        NoDeclaration().get_permissions()
    with pytest.raises(RuntimeError, match="AllowAny"):
        BadPublic().get_permissions()
    with pytest.raises(RuntimeError, match="IsAuthenticated alone"):
        AuthOnly().get_permissions()


def test_tenant_model_viewset_permission_guards_are_fail_closed():
    class NoDeclaration(TenantScopedModelViewSet):
        pass

    class BadPublic(TenantScopedModelViewSet):
        permission_classes = [AllowAny]

    class AuthOnly(TenantScopedModelViewSet):
        permission_classes = [IsAuthenticated]

    with pytest.raises(RuntimeError, match="explicitly declare"):
        NoDeclaration().get_permissions()
    with pytest.raises(RuntimeError, match="AllowAny"):
        BadPublic().get_permissions()
    with pytest.raises(RuntimeError, match="IsAuthenticated alone"):
        AuthOnly().get_permissions()


def test_tenant_readonly_viewset_permission_guards_are_fail_closed():
    class NoDeclaration(TenantScopedViewSet):
        pass

    class BadPublic(TenantScopedViewSet):
        permission_classes = [AllowAny]

    class AuthOnly(TenantScopedViewSet):
        permission_classes = [IsAuthenticated]

    with pytest.raises(RuntimeError, match="explicitly declare"):
        NoDeclaration().get_permissions()
    with pytest.raises(RuntimeError, match="AllowAny"):
        BadPublic().get_permissions()
    with pytest.raises(RuntimeError, match="IsAuthenticated alone"):
        AuthOnly().get_permissions()


@pytest.mark.django_db
class TestStabilityCoverage:
    def test_allowed_transition_matrix_covers_all_stability_aggregates(self):
        view = StabilityTenantViewSet()
        assert view.allowed_transitions(ProtocolVersion())["draft"] == {"approved"}
        assert view.allowed_transitions(SpecificationVersion())["approved"] == {"effective", "superseded"}
        assert view.allowed_transitions(StabilityStudy())["draft"] == {"planned", "canceled"}
        assert view.allowed_transitions(StudyTimepoint())["planned"] == {"open", "canceled"}
        assert view.allowed_transitions(StabilitySample())["stored"] == {"pulled", "disposed", "retained"}
        assert view.allowed_transitions(StorageCondition()) == {}

    def test_storage_condition_transition_rejects_invalid_target(self):
        user = QAManagerFactory()
        organization = user.memberships.select_related("organization").get().organization
        condition = StorageCondition.objects.create(
            organization=organization,
            created_by=user,
            code="25C",
            name="25 C / 60 RH",
        )
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post(
            f"/api/v1/stability/storage-conditions/{condition.id}/transition/",
            {"status": "approved", "comments": "Not a valid lifecycle target."},
            format="json",
        )
        assert response.status_code == 400

    def test_protocol_version_can_be_approved_with_signature(self):
        user = QAManagerFactory()
        organization = user.memberships.select_related("organization").get().organization
        product = ProductFactory(organization=organization, created_by=user)
        protocol = Protocol.objects.create(
            organization=organization,
            created_by=user,
            code="P-COV",
            name="Coverage Protocol",
            product=product,
            study_type="long_term",
        )
        version = ProtocolVersion.objects.create(
            organization=organization,
            created_by=user,
            protocol=protocol,
            version="1.0",
        )
        from services.signature_service import SignatureService

        token = SignatureService.issue(user)
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post(
            f"/api/v1/stability/protocol-versions/{version.id}/transition/",
            {"status": "approved", "comments": "Approved after QA review."},
            format="json",
            HTTP_X_SIGNATURE_TOKEN=token,
        )
        assert response.status_code == 200
        version.refresh_from_db()
        assert version.status == "approved"


@pytest.mark.django_db
def test_notification_task_creates_and_deduplicates_due_and_overdue_notifications():
    owner = UserFactory()
    organization = owner.memberships.select_related("organization").get().organization
    product = ProductFactory(organization=organization, created_by=owner)
    batch = Batch.objects.create(
        organization=organization,
        created_by=owner,
        product=product,
        batch_number="TASK-COVERAGE-001",
        mfg_date=timezone.localdate() - timedelta(days=30),
        expiry_date=timezone.localdate() + timedelta(days=365),
        incubation_date=timezone.localdate() - timedelta(days=30),
        study_type="long_term",
        status="active",
        shelf="TASK",
        rack="1",
        position="1",
        qty_placed=10,
        qty_remaining=10,
    )
    from apps.accounts.tests.factories import SupervisorFactory
    supervisor = SupervisorFactory()
    today = timezone.localdate()
    TestPointFactory(batch=batch, organization=organization, created_by=owner, status="pending", scheduled_date=today, month=1)
    TestPointFactory(batch=batch, organization=organization, created_by=owner, status="overdue", scheduled_date=today - timedelta(days=2), month=3)

    first = notify_upcoming_and_overdue_test_points.delay().get(timeout=10)
    assert first == 2
    assert Notification.objects.filter(organization=organization, user=supervisor).count() == 2

    second = notify_upcoming_and_overdue_test_points.delay().get(timeout=10)
    assert second == 0
    assert Notification.objects.filter(organization=organization, user=supervisor).count() == 2
