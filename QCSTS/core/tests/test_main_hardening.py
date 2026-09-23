import pytest
from datetime import timedelta
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils import timezone
from rest_framework.test import APIClient, APIRequestFactory
from rest_framework.exceptions import NotFound
from rest_framework.exceptions import PermissionDenied as DRFPermissionDenied

from apps.accounts.models import CustomUser
from apps.accounts.serializers import UserSerializer
from apps.accounts.tests.factories import QAManagerFactory, UserFactory
from apps.batches.models import Batch
from apps.batches.tests.factories import BatchFactory
from apps.billing.models import Plan, Subscription
from apps.audit.models import AuditLog
from apps.compliance.models import ElectronicSignature
from apps.platform.models import Membership, Organization, Role, Site
from apps.platform.services import TenantContextService
from apps.products.tests.factories import ProductFactory
from apps.stability.models import StorageCondition
from apps.quality.models import Deviation
from core.permissions import DenyTenantAction, IsAdmin


def make_org_user(slug, role_name="admin"):
    organization = Organization.objects.create(
        name=slug.title(),
        slug=slug,
        country="EG",
        timezone="Africa/Cairo",
        currency="EGP",
    )
    user = UserFactory(email=f"{role_name}@{slug}.test", role=role_name)
    Membership.objects.filter(user=user).delete()
    role, _ = Role.objects.get_or_create(organization=organization, name=role_name)
    membership = Membership.objects.create(
        user=user,
        organization=organization,
        role=role,
    )
    plan, _ = Plan.objects.get_or_create(
        code=Plan.Code.ESSENTIAL,
        defaults={
            "name": "Essential",
            "description": "Test plan",
            "monthly_price": 399,
            "annual_price": 3990,
            "currency": "EGP",
            "max_users": 1000,
            "max_sites": 100,
            "max_studies": 1000,
            "max_storage_mb": 100000,
            "api_access": True,
        },
    )
    now = timezone.now()
    Subscription.objects.get_or_create(
        organization=organization,
        status=Subscription.Status.TRIALING,
        defaults={
            "plan": plan,
            "interval": Subscription.Interval.MONTH,
            "provider": "test",
            "trial_ends_at": now + timedelta(days=30),
            "current_period_start": now,
            "current_period_end": now + timezone.timedelta(days=30),
        },
    )
    return organization, user, membership


@pytest.mark.django_db
def test_every_base_model_has_active_and_all_object_managers():
    from django.apps import apps
    from core.models import ActiveManager, BaseModel

    for model in apps.get_models():
        if model._meta.abstract or not issubclass(model, BaseModel):
            continue

        assert isinstance(
            model._default_manager,
            ActiveManager,
        ), f"{model.__name__} must hide inactive rows through its default manager."
        assert hasattr(
            model,
            "all_objects",
        ), f"{model.__name__} must expose an all_objects manager for audit/history access."


@pytest.mark.django_db
def test_membership_save_rejects_role_from_another_organization():
    organization_a, user, _ = make_org_user("membership-a")
    organization_b, _, _ = make_org_user("membership-b")
    role_b = Role.objects.get(organization=organization_b, name="admin")
    Membership.objects.filter(user=user).delete()

    with pytest.raises(ValidationError, match="role must belong"):
        Membership.objects.create(
            user=user,
            organization=organization_a,
            role=role_b,
        )


@pytest.mark.django_db
def test_membership_save_rejects_default_site_from_another_organization():
    organization_a, user, _ = make_org_user("site-membership-a")
    organization_b, _, _ = make_org_user("site-membership-b")
    role_a = Role.objects.get(organization=organization_a, name="admin")
    foreign_site = Site.objects.create(
        organization=organization_b,
        name="Foreign Site",
        country="EG",
    )
    Membership.objects.filter(user=user).delete()

    with pytest.raises(ValidationError, match="default site"):
        Membership.objects.create(
            user=user,
            organization=organization_a,
            role=role_a,
            default_site=foreign_site,
        )


@pytest.mark.django_db
def test_selected_site_requires_explicit_membership():
    user = UserFactory()
    membership = user.memberships.select_related("organization").get()
    organization = membership.organization
    allowed = Site.objects.create(
        organization=organization,
        name="Allowed Site",
        country="EG",
    )
    forbidden = Site.objects.create(
        organization=organization,
        name="Forbidden Site",
        country="EG",
    )
    membership.default_site = allowed
    membership.save()
    membership.sites.add(allowed)

    request = APIRequestFactory().get(
        "/",
        HTTP_X_SITE_ID=str(forbidden.id),
    )
    request.user = user

    with pytest.raises(DRFPermissionDenied, match="access to this site"):
        TenantContextService.resolve(request)

    membership.sites.add(forbidden)
    request = APIRequestFactory().get("/", HTTP_X_SITE_ID=str(forbidden.id))
    request.user = user
    TenantContextService.resolve(request)
    assert request.site == forbidden


@pytest.mark.django_db
def test_default_site_must_also_be_an_explicit_membership():
    user = UserFactory()
    membership = user.memberships.select_related("organization").get()
    site = Site.objects.create(
        organization=membership.organization,
        name="Unassigned Default",
        country="EG",
    )
    membership.default_site = site
    membership.save()

    request = APIRequestFactory().get("/")
    request.user = user

    TenantContextService.resolve(request)
    assert request.site is None


@pytest.mark.django_db
def test_explicit_inactive_site_is_rejected():
    user = UserFactory()
    membership = user.memberships.select_related("organization").get()
    site = Site.objects.create(
        organization=membership.organization,
        name="Inactive Explicit",
        country="EG",
        status=Site.Status.INACTIVE,
    )
    membership.sites.add(site)

    request = APIRequestFactory().get(
        "/",
        HTTP_X_SITE_ID=str(site.id),
    )
    request.user = user

    with pytest.raises(NotFound, match="Active site"):
        TenantContextService.resolve(request)


@pytest.mark.django_db
def test_inactive_default_site_is_not_returned_as_tenant_context():
    user = UserFactory()
    membership = user.memberships.select_related("organization").get()
    organization = membership.organization
    site = Site.objects.create(
        organization=organization,
        name="Inactive Default",
        country="EG",
        status=Site.Status.INACTIVE,
    )
    membership.default_site = site
    membership.save()

    request = APIRequestFactory().get("/")
    request.user = user

    TenantContextService.resolve(request)
    assert request.organization == organization
    assert request.site is None


@pytest.mark.django_db
def test_corrupt_mfa_ciphertext_fails_closed():
    user = UserFactory()
    user.mfa_enabled = True
    user.mfa_secret_encrypted = "not-valid-fernet-data"
    user.save(update_fields=["mfa_enabled", "mfa_secret_encrypted"])

    assert user.get_mfa_secret() is None
    assert user.verify_totp("123456", timestamp=0) is False


@pytest.mark.django_db
def test_custom_user_role_never_grants_admin_authority():
    user = UserFactory(role="analyst")
    membership = user.memberships.select_related("role").get()
    assert membership.role.name == "analyst"

    user.role = "admin"
    user.save(update_fields=["role"])

    request = APIRequestFactory().get("/")
    request.user = user
    request.membership = membership
    assert IsAdmin().has_permission(request, object()) is False


@pytest.mark.django_db
def test_user_serializer_hides_revoked_membership_context():
    user = UserFactory()
    membership = user.memberships.select_related("organization").get()
    organization = membership.organization
    site = Site.objects.create(
        organization=organization,
        name="Default QC Site",
        country="EG",
    )
    membership.default_site = site
    membership.sites.add(site)
    membership.save(update_fields=["default_site"])

    membership.is_active = False
    membership.save(update_fields=["is_active"])

    data = UserSerializer(user, context={"organization": organization}).data
    assert data["organization_role"] is None
    assert data["organization_site"] is None


@pytest.mark.django_db
def test_stability_status_cannot_be_changed_through_normal_patch():
    user = QAManagerFactory()
    organization = user.memberships.select_related("organization").get().organization
    condition = StorageCondition.objects.create(
        organization=organization,
        code="25C",
        name="25C / 60% RH",
    )

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.patch(
        f"/api/v1/stability/storage-conditions/{condition.id}/",
        {"status": "approved"},
        format="json",
    )

    assert response.status_code == 400
    condition.refresh_from_db()
    assert condition.status == "draft"


@pytest.mark.django_db
def test_sample_pull_rejects_test_point_from_different_batch():
    user = UserFactory()
    organization = user.memberships.select_related("organization").get().organization

    product_a = ProductFactory(organization=organization, created_by=user)
    product_b = ProductFactory(organization=organization, created_by=user)
    batch_a = BatchFactory(
        organization=organization,
        created_by=user,
        product=product_a,
    )
    batch_b = BatchFactory(
        organization=organization,
        created_by=user,
        product=product_b,
    )
    foreign_test_point = batch_b.test_points.first()

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(
        "/api/v1/chamber/pulls/",
        {
            "batch": str(batch_a.id),
            "test_point": str(foreign_test_point.id),
            "qty_pulled": 1,
        },
        format="json",
    )

    assert response.status_code == 400
    batch_a.refresh_from_db()
    assert batch_a.qty_remaining == batch_a.qty_placed
    assert not Batch.objects.filter(pk=batch_a.id, qty_remaining__lt=batch_a.qty_placed).exists()


@pytest.mark.django_db
def test_batch_model_enforces_date_and_quantity_invariants():
    user = UserFactory()
    organization = user.memberships.select_related("organization").get().organization
    product = ProductFactory(organization=organization, created_by=user)

    with pytest.raises(ValidationError, match="Expiry date"):
        Batch.objects.create(
            organization=organization,
            created_by=user,
            product=product,
            batch_number="INVALID-DATE-1",
            mfg_date="2026-09-22",
            expiry_date="2026-09-21",
            incubation_date="2026-09-22",
            study_type="long_term",
            status="active",
            shelf="S1",
            rack="R1",
            position="P1",
            qty_placed=10,
            qty_remaining=10,
        )

    with pytest.raises(ValidationError, match="Remaining quantity"):
        Batch.objects.create(
            organization=organization,
            created_by=user,
            product=product,
            batch_number="INVALID-QTY-1",
            mfg_date="2026-09-22",
            expiry_date="2029-09-22",
            incubation_date="2026-09-22",
            study_type="long_term",
            status="active",
            shelf="S2",
            rack="R2",
            position="P2",
            qty_placed=10,
            qty_remaining=11,
        )


@pytest.mark.django_db
def test_soft_delete_rolls_back_audit_when_state_save_fails(monkeypatch):
    from apps.audit.models import AuditLog
    from apps.quality.models import Deviation
    from apps.accounts.tests.factories import UserFactory

    user = UserFactory()
    organization = user.memberships.select_related("organization").get().organization
    deviation = Deviation.objects.create(
        organization=organization,
        created_by=user,
        owner=user,
        reference="DELETE-ATOMIC-001",
        title="Atomic delete",
        description="Audit and retirement must commit together.",
        status="open",
    )

    before = AuditLog.objects.filter(
        organization=organization,
        object_id=deviation.id,
        action="DELETE",
    ).count()

    original_save = deviation.save

    def fail_save(*args, **kwargs):
        raise RuntimeError("simulated save failure")

    monkeypatch.setattr(deviation, "save", fail_save)

    with pytest.raises(RuntimeError, match="simulated save failure"):
        deviation.soft_delete(deleted_by=user)

    deviation.refresh_from_db()
    assert deviation.is_active is True
    assert (
        AuditLog.objects.filter(
            organization=organization,
            object_id=deviation.id,
            action="DELETE",
        ).count()
        == before
    )



@pytest.mark.django_db
def test_tenant_domain_delete_soft_deactivates_record():
    user = QAManagerFactory()
    organization = user.memberships.select_related("organization").get().organization
    deviation = Deviation.objects.create(
        organization=organization,
        created_by=user,
        owner=user,
        reference="DEL-HARDEN-001",
        title="Delete hardening",
        description="Verify API deletion is a soft retirement.",
        status="open",
    )

    client = APIClient()
    client.force_authenticate(user=user)
    client.credentials(HTTP_X_ORGANIZATION_ID=str(organization.id))
    response = client.delete(f"/api/v1/quality/deviations/{deviation.id}/")

    assert response.status_code == 204
    deviation.refresh_from_db()
    assert deviation.is_active is False
    assert deviation.id not in Deviation.objects.values_list("id", flat=True)
    assert deviation.id in Deviation.all_objects.values_list("id", flat=True)


@pytest.mark.django_db
def test_cross_tenant_protocol_product_reference_is_rejected_before_create():
    organization_a, user_a, _ = make_org_user("protocol-a", "analyst")
    organization_b, user_b, _ = make_org_user("protocol-b", "analyst")
    product = ProductFactory(organization=organization_a, created_by=user_a)

    client = APIClient()
    client.force_authenticate(user=user_b)
    client.credentials(HTTP_X_ORGANIZATION_ID=str(organization_b.id))

    response = client.post(
        "/api/v1/stability/protocols/",
        {
            "code": "FOREIGN-PROTOCOL",
            "name": "Foreign reference",
            "product": str(product.id),
            "study_type": "long_term",
        },
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_invoice_rejects_cross_organization_subscription():
    from decimal import Decimal
    from django.core.exceptions import ValidationError
    from apps.billing.models import Invoice, Plan, Subscription

    organization_a, user_a, _ = make_org_user("invoice-a")
    organization_b, _, _ = make_org_user("invoice-b")

    subscription_b = Subscription.objects.get(organization=organization_b)

    with pytest.raises(ValidationError, match="Invoice subscription"):
        Invoice.objects.create(
            organization=organization_a,
            subscription=subscription_b,
            number="INV-CROSS-ORG-001",
            currency="USD",
            subtotal=Decimal("100.00"),
            total=Decimal("100.00"),
        )


@pytest.mark.django_db
def test_password_change_revokes_existing_jwt_sessions():
    user = CustomUser.objects.create_user(
        email="session-hardening@qcsts.test",
        password="Initial-password-123",
        full_name="Session Hardening",
        role="analyst",
    )
    from apps.accounts.security import issue_tokens
    refresh = issue_tokens(user)
    access = str(refresh.access_token)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    response = client.post(
        "/api/v1/auth/change-password/",
        {
            "current_password": "Initial-password-123",
            "new_password": "Replacement-password-456",
        },
        format="json",
    )
    assert response.status_code == 200

    protected = client.get("/api/v1/auth/me/")
    assert protected.status_code == 401

    refresh_response = APIClient().post(
        "/api/v1/auth/token/refresh/",
        {"refresh": str(refresh)},
        format="json",
    )
    assert refresh_response.status_code == 401


@pytest.mark.django_db
def test_membership_cannot_add_foreign_organization_site():
    organization_a, user, membership = make_org_user("membership-sites-a")
    organization_b, _, _ = make_org_user("membership-sites-b")
    foreign_site = Site.objects.create(
        organization=organization_b,
        name="Foreign Membership Site",
        country="EG",
    )

    with pytest.raises(ValidationError, match="membership organization"):
        membership.sites.add(foreign_site)


@pytest.mark.django_db
def test_quality_unknown_action_fails_closed():
    from apps.quality.views import QualityTenantViewSet

    view = QualityTenantViewSet()
    view.action = "future_action"
    view.request = APIRequestFactory().get("/")
    permissions = view.get_permissions()
    assert len(permissions) == 1
    assert isinstance(permissions[0], DenyTenantAction)
    assert permissions[0].has_permission(view.request, view) is False


@pytest.mark.django_db
def test_stability_unknown_action_fails_closed():
    from apps.stability.api import StabilityTenantViewSet

    view = StabilityTenantViewSet()
    view.action = "future_action"
    view.request = APIRequestFactory().get("/")
    permissions = view.get_permissions()
    assert len(permissions) == 1
    assert permissions[0].has_permission(view.request, view) is False


@pytest.mark.django_db
def test_audit_actor_must_belong_to_audit_organization():
    organization_a, _, _ = make_org_user("audit-org-a")
    _, user_b, _ = make_org_user("audit-org-b")

    with pytest.raises(ValidationError, match="audit actor"):
        AuditLog.objects.create(
            organization=organization_a,
            performed_by=user_b,
            action="UPDATE",
            model_name="Batch",
            object_id="1",
            object_repr="foreign actor",
        )


@pytest.mark.django_db
def test_soft_delete_rolls_back_when_audit_write_fails(monkeypatch):
    user = QAManagerFactory()
    organization = user.memberships.select_related("organization").get().organization
    deviation = Deviation.objects.create(
        organization=organization,
        created_by=user,
        owner=user,
        reference="DELETE-AUDIT-FAIL-001",
        title="Audit failure",
        description="Audit failure must prevent retirement.",
        status="open",
    )

    def fail_audit(*args, **kwargs):
        raise RuntimeError("simulated audit failure")

    monkeypatch.setattr("apps.audit.models.AuditLog.objects.create", fail_audit)

    with pytest.raises(Exception):
        deviation.soft_delete(deleted_by=user)

    deviation.refresh_from_db()
    assert deviation.is_active is True


@pytest.mark.django_db
def test_electronic_signature_requires_signer_membership():
    organization_a, _, _ = make_org_user("signature-a")
    _, signer, _ = make_org_user("signature-b")

    with pytest.raises(PermissionDenied, match="active member"):
        ElectronicSignature.issue(
            organization=organization_a,
            signer=signer,
            record_type="TestResult",
            record_id="00000000-0000-0000-0000-000000000001",
            record_version="1",
            meaning=ElectronicSignature.Meaning.REVIEW,
            reason="Cross-tenant signer test",
            authentication_secret="test-secret",
        )