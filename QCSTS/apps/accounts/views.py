from django.db import transaction
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.throttling import AnonRateThrottle, ScopedRateThrottle
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import CustomUser
from apps.accounts.serializers import (
    ChangePasswordSerializer,
    CreateUserSerializer,
    LoginSerializer,
    OrganizationRegistrationSerializer,
    UserSerializer,
)
from apps.platform.models import Membership, Organization, Permission, Role, Site
from core.permissions import IsAdmin
from core.responses import error_response, success_response
from core.views import PublicAPIView, TenantExemptAPIView, TenantScopedAPIView
from services.audit_service import AuditService


class LoginView(PublicAPIView):
    """Authenticates a user before any tenant context exists."""

    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)
        ip = request.META.get("REMOTE_ADDR")
        user.last_login_ip = ip
        user.save(update_fields=["last_login_ip"])

        AuditService.log(
            performed_by=user, action="LOGIN", model_name="CustomUser",
            object_id=user.id, object_repr=str(user), ip_address=ip,
        )
        return success_response(
            data={
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserSerializer(user).data,
            }
        )


class RegisterView(PublicAPIView):
    """
    POST /api/v1/auth/register/

    Public SaaS onboarding endpoint. It creates the first user and exactly one
    organization membership in a single transaction. No caller can choose an
    arbitrary role: the first account is always the organization administrator.

    This is intentionally separate from POST /auth/users/, which remains an
    authenticated admin-only endpoint for adding staff to an existing tenant.
    """

    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]
    serializer_class = OrganizationRegistrationSerializer

    @transaction.atomic
    def post(self, request):
        serializer = OrganizationRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data.copy()

        organization = Organization.objects.create(
            name=data["organization_name"],
            legal_name=data.get("legal_name", ""),
            slug=data["slug"],
            country=data["country"],
            timezone=data.get("timezone", "UTC"),
            currency=data.get("currency", "USD"),
        )

        site = None
        if data.get("site_name"):
            site = Site.objects.create(
                organization=organization,
                name=data["site_name"],
                address=data.get("site_address", ""),
                country=data["country"],
                timezone=data.get("timezone", "UTC"),
            )

        user = CustomUser.objects.create_user(
            email=data["email"],
            password=data["password"],
            full_name=data["full_name"],
            role="admin",
        )

        role = Role.objects.create(
            organization=organization,
            name="admin",
            description="Organization administrator",
            is_system=False,
        )

        # The first administrator must be able to operate the tenant
        # immediately. These are the permissions currently used by platform
        # management; adding more permissions later remains an explicit RBAC
        # change rather than an implicit global superuser grant.
        admin_permission_codes = {
            "site.view": ("View sites", "View organization sites."),
            "site.create": ("Create sites", "Create organization sites."),
            "site.update": ("Update sites", "Update organization sites."),
            "site.delete": ("Delete sites", "Delete organization sites."),
        }
        for code, (name, description) in admin_permission_codes.items():
            permission, _ = Permission.objects.get_or_create(
                code=code, defaults={"name": name, "description": description}
            )
            role.permissions.add(permission)

        membership = Membership.objects.create(
            user=user,
            organization=organization,
            role=role,
            default_site=site,
        )
        if site:
            membership.sites.add(site)

        AuditService.log(
            performed_by=user,
            action="CREATE",
            model_name="Organization",
            object_id=organization.id,
            object_repr=str(organization),
            new_value={
                "organization": organization.name,
                "owner": user.email,
                "site": site.name if site else None,
            },
            ip_address=request.META.get("REMOTE_ADDR"),
            organization=organization,
        )

        refresh = RefreshToken.for_user(user)
        return success_response(
            data={
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserSerializer(
                    user, context={"organization": organization}
                ).data,
                "organization": {
                    "id": str(organization.id),
                    "name": organization.name,
                    "legal_name": organization.legal_name,
                    "slug": organization.slug,
                    "country": organization.country,
                    "timezone": organization.timezone,
                    "currency": organization.currency,
                    "status": organization.status,
                },
                "site": (
                    {
                        "id": str(site.id),
                        "name": site.name,
                        "address": site.address,
                    }
                    if site else None
                ),
                "membership": {
                    "id": str(membership.id),
                    "role": role.name,
                    "organization_id": str(organization.id),
                    "site_id": str(site.id) if site else None,
                },
            },
            status_code=status.HTTP_201_CREATED,
        )


class LogoutView(TenantExemptAPIView):
    """Blacklists a refresh token; operates on the token, not an organization."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return error_response({"detail": "Refresh token is required."}, status.HTTP_400_BAD_REQUEST)
        try:
            RefreshToken(refresh_token).blacklist()
        except TokenError:
            return error_response({"detail": "Invalid or expired token."}, status.HTTP_400_BAD_REQUEST)

        AuditService.log(
            performed_by=request.user, action="LOGOUT", model_name="CustomUser",
            object_id=request.user.id, object_repr=str(request.user),
            ip_address=request.META.get("REMOTE_ADDR"),
        )
        return success_response(message="Logged out successfully.")


class MeView(TenantExemptAPIView):
    """Returns the caller's own identity, independent of any selected tenant."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return success_response(data=UserSerializer(request.user).data)


class ChangePasswordView(TenantExemptAPIView):
    """Changes the caller's own credential; not an organization-scoped resource."""

    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password"])
        return success_response(message="Password changed successfully.")


class UserListCreateView(TenantScopedAPIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        users = (
            CustomUser.objects.filter(
                memberships__organization=request.organization,
                memberships__is_active=True,
            )
            .distinct()
            .order_by("-created_at")
        )
        return success_response(
            data=UserSerializer(
                users, many=True, context={"organization": request.organization}
            ).data
        )

    @transaction.atomic
    def post(self, request):
        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        role_name = data.pop("role", "analyst")

        user = CustomUser.objects.create_user(**data, role=role_name)

        role, _ = Role.objects.get_or_create(
            organization=request.organization, name=role_name
        )
        Membership.objects.create(user=user, organization=request.organization, role=role)

        AuditService.log(
            performed_by=request.user, action="CREATE", model_name="CustomUser",
            object_id=user.id, object_repr=str(user),
            new_value={"email": user.email, "role": role_name},
            ip_address=request.META.get("REMOTE_ADDR"),
            organization=request.organization,
        )
        return success_response(
            data=UserSerializer(user, context={"organization": request.organization}).data,
            status_code=status.HTTP_201_CREATED,
        )


class UserDetailView(TenantScopedAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]

    def get_membership(self, pk):
        return (
            Membership.objects.select_related("user", "role")
            .filter(user_id=pk, organization=self.request.organization)
            .first()
        )

    def get(self, request, pk):
        membership = self.get_membership(pk)
        if not membership:
            return error_response({"detail": "User not found."}, status.HTTP_404_NOT_FOUND)
        return success_response(
            data=UserSerializer(
                membership.user, context={"organization": request.organization}
            ).data
        )

    def patch(self, request, pk):
        membership = self.get_membership(pk)
        if not membership:
            return error_response({"detail": "User not found."}, status.HTTP_404_NOT_FOUND)

        before = {"full_name": membership.user.full_name}
        serializer = UserSerializer(
            membership.user, data=request.data, partial=True,
            context={"organization": request.organization},
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        AuditService.log(
            performed_by=request.user, action="UPDATE", model_name="CustomUser",
            object_id=user.id, object_repr=str(user),
            old_value=before, new_value={"full_name": user.full_name},
            ip_address=request.META.get("REMOTE_ADDR"),
            organization=request.organization,
        )
        return success_response(
            data=UserSerializer(user, context={"organization": request.organization}).data
        )

    def delete(self, request, pk):
        membership = self.get_membership(pk)
        if not membership:
            return error_response({"detail": "User not found."}, status.HTTP_404_NOT_FOUND)
        if membership.user_id == request.user.id:
            return error_response(
                {"detail": "You cannot revoke your own membership."},
                status.HTTP_400_BAD_REQUEST,
            )

        membership.is_active = False
        membership.save(update_fields=["is_active"])

        AuditService.log(
            performed_by=request.user, action="DELETE", model_name="Membership",
            object_id=membership.id, object_repr=str(membership),
            old_value={"is_active": True}, new_value={"is_active": False},
            ip_address=request.META.get("REMOTE_ADDR"),
            organization=request.organization,
        )
        return success_response(message="Organization access revoked.")