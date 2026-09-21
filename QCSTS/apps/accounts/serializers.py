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
    deactivated account — returns the SAME 401.
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
    """Read view of a user. Authority comes from Membership.role."""

    organization_role = serializers.SerializerMethodField()
    organization_site = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            "id", "email", "full_name", "role", "organization_role", "organization_site",
            "is_active", "created_at",
        ]
        read_only_fields = ["id", "email", "role", "organization_role", "created_at"]

    def get_organization_role(self, obj):
        organization = self.context.get("organization")
        if organization is None:
            return None
        membership = obj.memberships.filter(organization=organization).select_related("role").first()
        return membership.role.name if membership else None

    def get_organization_site(self, obj):
        organization = self.context.get("organization")
        if organization is None:
            return None
        membership = obj.memberships.filter(organization=organization).select_related("default_site").first()
        if not membership or not membership.default_site:
            return None
        return {"id": str(membership.default_site.id), "name": membership.default_site.name}


class CreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=12)
    role = serializers.CharField(write_only=True, required=False, default="analyst")

    class Meta:
        model = CustomUser
        fields = ["email", "full_name", "role", "password"]

    def validate_role(self, value):
        allowed_roles = {"viewer", "analyst", "supervisor", "qa_manager", "admin"}

        value = (value or "").strip().lower()
        if value not in allowed_roles:
            raise serializers.ValidationError(
                f"Unknown role. Choose one of: {', '.join(sorted(allowed_roles))}."
            )
        return value

    def validate_email(self, value):
        if CustomUser.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value


class OrganizationRegistrationSerializer(serializers.Serializer):
    """
    Public first-tenant bootstrap.

    Creates exactly one organization, its first site (when supplied), the
    registering user, an organization-scoped admin role, and a membership.
    Everything is committed atomically by RegisterView.
    """

    organization_name = serializers.CharField(max_length=255)
    legal_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    slug = serializers.SlugField(max_length=80, required=False, allow_blank=True)
    country = serializers.CharField(max_length=2)
    timezone = serializers.CharField(max_length=64, default="UTC")
    currency = serializers.CharField(max_length=3, default="USD")
    site_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    site_address = serializers.CharField(required=False, allow_blank=True)

    full_name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=12, trim_whitespace=False)

    def validate_country(self, value):
        return value.strip().upper()

    def validate_currency(self, value):
        return value.strip().upper()

    def validate_email(self, value):
        if CustomUser.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()

    def validate_slug(self, value):
        value = value.strip().lower()
        if value and __import__("apps.platform.models", fromlist=["Organization"]).Organization.objects.filter(slug=value).exists():
            raise serializers.ValidationError("This organization slug is already in use.")
        return value

    def validate(self, attrs):
        from django.utils.text import slugify

        if not attrs.get("slug"):
            slug = slugify(attrs["organization_name"])[:80]
            from apps.platform.models import Organization
            if Organization.objects.filter(slug=slug).exists():
                raise serializers.ValidationError(
                    {"slug": "An organization with this name already exists; provide a unique slug."}
                )
            attrs["slug"] = slug
        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=12, trim_whitespace=False)


class VerifyEmailSerializer(serializers.Serializer):
    token = serializers.CharField()
