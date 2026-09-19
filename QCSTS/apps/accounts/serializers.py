from django.contrib.auth.hashers import check_password, make_password
from rest_framework import serializers

from apps.accounts.models import CustomUser
from core.exceptions import InvalidCredentialsError

_DUMMY_HASH = make_password("qcsts-timing-equaliser")


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, data):
        user = CustomUser.objects.filter(email=data.get("email")).first()
        password = data.get("password")
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
        if not self.context["request"].user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate(self, data):
        if data["current_password"] == data["new_password"]:
            raise serializers.ValidationError(
                {"new_password": "The new password must differ from the current one."}
            )
        return data


class UserSerializer(serializers.ModelSerializer):
    organization = serializers.SerializerMethodField()
    site = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    role_scope = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            "id", "email", "full_name", "organization", "site", "role",
            "role_scope", "is_active", "created_at",
        ]
        read_only_fields = fields

    def _membership(self, obj):
        try:
            membership = obj.membership
        except CustomUser.membership.RelatedObjectDoesNotExist:
            return None
        if not membership.is_active:
            return None
        organization = self.context.get("organization")
        if organization is not None and membership.organization_id != organization.id:
            return None
        return membership

    def get_organization(self, obj):
        membership = self._membership(obj)
        return {"id": str(membership.organization_id), "name": membership.organization.name} if membership else None

    def get_site(self, obj):
        membership = self._membership(obj)
        return {"id": str(membership.site_id), "name": membership.site.name} if membership else None

    def get_role(self, obj):
        membership = self._membership(obj)
        return membership.role.name if membership else None

    def get_role_scope(self, obj):
        membership = self._membership(obj)
        return membership.role.scope if membership else None


class CreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=12)
    role = serializers.CharField(write_only=True, required=True)
    site_id = serializers.UUIDField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ["email", "full_name", "role", "site_id", "password"]

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
        return value.lower()


class OrganizationRegistrationSerializer(serializers.Serializer):
    organization_name = serializers.CharField(max_length=255)
    legal_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    slug = serializers.SlugField(max_length=80, required=False, allow_blank=True)
    country = serializers.CharField(max_length=2)
    timezone = serializers.CharField(max_length=64, default="UTC")
    currency = serializers.CharField(max_length=3, default="USD")
    site_name = serializers.CharField(max_length=255)
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
        from apps.platform.models import Organization
        if not attrs.get("slug"):
            slug = slugify(attrs["organization_name"])[:80]
            if Organization.objects.filter(slug=slug).exists():
                raise serializers.ValidationError(
                    {"slug": "An organization with this name already exists; provide a unique slug."}
                )
            attrs["slug"] = slug
        return attrs
