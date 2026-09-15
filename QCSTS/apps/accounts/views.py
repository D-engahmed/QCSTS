from django.db import transaction
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import CustomUser
from apps.accounts.serializers import (
    ChangePasswordSerializer,
    CreateUserSerializer,
    LoginSerializer,
    UserSerializer,
)
from apps.platform.models import Membership, Role
from core.permissions import IsAdmin
from core.responses import error_response, success_response
from core.views import PublicAPIView, TenantExemptAPIView, TenantScopedAPIView
from services.audit_service import AuditService


class LoginView(PublicAPIView):
    """
    POST /api/v1/auth/login/

    Tenant exempt: the caller has no organization context until they are
    authenticated. Throttled, because the account-lockout rule alone is not a
    brute-force defence — it is a denial-of-service lever if the attacker can
    hammer it for free.
    """

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
            performed_by=user,
            action="LOGIN",
            model_name="CustomUser",
            object_id=user.id,
            object_repr=str(user),
            ip_address=ip,
        )

        return success_response(
            data={
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserSerializer(user).data,
            },
            status_code=status.HTTP_200_OK,
        )


class LogoutView(TenantExemptAPIView):
    """POST /api/v1/auth/logout/ — blacklists the refresh token. No org context needed."""

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
            performed_by=request.user,
            action="LOGOUT",
            model_name="CustomUser",
            object_id=request.user.id,
            object_repr=str(request.user),
            ip_address=request.META.get("REMOTE_ADDR"),
        )
        return success_response(message="Logged out successfully.")


class MeView(TenantExemptAPIView):
    """GET /api/v1/auth/me/ — a user reading their own record, across all their orgs."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return success_response(data=UserSerializer(request.user).data)


class ChangePasswordView(TenantExemptAPIView):
    """POST /api/v1/auth/change-password/ — self-service, no org context needed."""

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
    """
    GET  /api/v1/auth/users/  — users who hold a membership in the ACTIVE org.
    POST /api/v1/auth/users/  — create a user and grant them membership here.

    This endpoint previously returned CustomUser.objects.all(): every user of
    every tenant, with names and email addresses, to anyone holding the global
    "admin" string. That was the platform's largest cross-tenant leak.
    """

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
        Membership.objects.create(
            user=user, organization=request.organization, role=role
        )

        AuditService.log(
            performed_by=request.user,
            action="CREATE",
            model_name="CustomUser",
            object_id=user.id,
            object_repr=str(user),
            new_value={"email": user.email, "role": role_name},
            ip_address=request.META.get("REMOTE_ADDR"),
            organization=request.organization,
        )
        return success_response(
            data=UserSerializer(user, context={"organization": request.organization}).data,
            status_code=status.HTTP_201_CREATED,
        )


class UserDetailView(TenantScopedAPIView):
    """
    GET    /api/v1/auth/users/<id>/  — org-scoped read
    PATCH  /api/v1/auth/users/<id>/  — profile fields only; role is read-only
    DELETE /api/v1/auth/users/<id>/  — revokes membership in the ACTIVE org

    DELETE no longer sets user.is_active=False. In a multi-tenant platform an
    admin at company A must not be able to disable a person's access at
    company B. Revoking the membership is the correct blast radius.

    Role changes are deliberately NOT available here. They need their own
    audited, signature-backed endpoint (see the "Permission changes" audit item
    in the gap checklist); a writable role on a profile PATCH was how privilege
    escalation got in last time.
    """

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
            membership.user,
            data=request.data,
            partial=True,
            context={"organization": request.organization},
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        AuditService.log(
            performed_by=request.user,
            action="UPDATE",
            model_name="CustomUser",
            object_id=user.id,
            object_repr=str(user),
            old_value=before,
            new_value={"full_name": user.full_name},
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
            performed_by=request.user,
            action="DELETE",
            model_name="Membership",
            object_id=membership.id,
            object_repr=str(membership),
            old_value={"is_active": True},
            new_value={"is_active": False},
            ip_address=request.META.get("REMOTE_ADDR"),
            organization=request.organization,
        )
        return success_response(message="Organization access revoked.")
