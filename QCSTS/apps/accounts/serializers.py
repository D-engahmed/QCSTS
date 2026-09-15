from django.contrib.auth.hashers import check_password, make_password
from rest_framework import serializers

from apps.accounts.models import CustomUser
from core.exceptions import InvalidCredentialsError

# Burned once on every unknown-email login so that the response time does not
# reveal whether the address exists. Computed at import, never used as a secret.
_DUMMY_HASH = make_password("qcsts-timing-equaliser")


class LoginSerializer(serializers.Serializer):
    """
    Validates email + password at /api/v1/auth/login/.

    Every failure mode — unknown email, wrong password, locked account,
    deactivated account — returns the SAME 401. The previous version returned
    400 / 401 / 403 respectively, which let an unauthenticated caller confirm
    that an address existed and read its account state. That is an
    enumeration oracle on a customer's staff directory.
    """

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        user = CustomUser.objects.filter(email=email).first()

        if user is None:
            check_password(password, _DUMMY_HASH)
            raise InvalidCredentialsError()

        if not user.is_active or user.is_locked_out:
            check_password(password, _DUMMY_HASH)
            raise InvalidCredentialsError()

        if not user.check_password(password):
            user.register_failed_login()
            raise InvalidCredentialsError()

        user.reset_failed_attempts()
        data["user"] = user
        return data


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True, trim_whitespace=False)
    new_password = serializers.CharField(write_only=True, min_length=12, trim_whitespace=False)

    def validate_current_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate(self, data):
        if data["current_password"] == data["new_password"]:
            raise serializers.ValidationError(
                {"new_password": "The new password must differ from the current one."}
            )
        return data


class UserSerializer(serializers.ModelSerializer):
    """
    Read view of a user.

    ``role`` is READ ONLY. It was previously writable through
    UserDetailView.patch, so any admin could set any user's role to "admin" —
    privilege escalation in one PATCH. Authority now lives on Membership.role
    (see core.permissions); this field is a display mirror only and changing it
    grants nothing.
    """

    organization_role = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "full_name",
            "role",
            "organization_role",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "email", "role", "organization_role", "created_at"]

    def get_organization_role(self, obj):
        """The role that actually governs access, within the active organization."""
        organization = self.context.get("organization")
        if organization is None:
            return None
        membership = obj.memberships.filter(organization=organization).select_related("role").first()
        return membership.role.name if membership else None


class CreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=12)
    role = serializers.CharField(write_only=True, required=False, default="analyst")

    class Meta:
        model = CustomUser
        fields = ["email", "full_name", "role", "password"]

    def validate_role(self, value):
        from core.permissions import ROLE_RANK

        value = (value or "").strip().lower()
        if value not in ROLE_RANK:
            raise serializers.ValidationError(
                f"Unknown role. Choose one of: {', '.join(sorted(ROLE_RANK))}."
            )
        return value

    def validate_email(self, value):
        if CustomUser.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
