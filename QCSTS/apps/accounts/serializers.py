from rest_framework import serializers
from apps.accounts.models import CustomUser
from core.exceptions import AccountLockedError, InvalidCredentialsError


class LoginSerializer(serializers.Serializer):
    """
    Validates email + password at /api/v1/auth/login/.

    - Unknown email            -> plain ValidationError (400)
    - Correct email, inactive  -> AccountLockedError (403)
    - Correct email, wrong pw  -> InvalidCredentialsError (401), also
                                   increments failed_login_attempts
                                   (5 strikes auto-deactivates the account)
    - Correct email + password -> validated_data["user"] is set,
                                   failed_login_attempts is reset to 0
    """

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password.")

        if not user.is_active:
            raise AccountLockedError()

        if not user.check_password(password):
            user.increment_failed_attempts()
            raise InvalidCredentialsError()

        user.reset_failed_attempts()
        data["user"] = user
        return data


class ChangePasswordSerializer(serializers.Serializer):
    """
    Validates a self-service password change at
    /api/v1/auth/change-password/. Requires the request's current
    user (passed in via context={"request": request}) to confirm
    their current password before setting a new one.
    """

    current_password = serializers.CharField(write_only=True, trim_whitespace=False)
    new_password = serializers.CharField(write_only=True, min_length=12, trim_whitespace=False)

    def validate_current_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "email", "full_name", "role", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]

class CreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=12)

    class Meta:
        model = CustomUser
        fields = ["email", "full_name", "role", "password"]

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)