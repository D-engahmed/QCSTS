from datetime import datetime, timezone
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed


class PasswordChangeAwareJWTAuthentication(JWTAuthentication):
    """Reject access tokens issued before the user's latest password change."""

    def authenticate(self, request):
        result = super().authenticate(request)
        if result is None:
            return None

        user, token = result
        changed_at = getattr(user, "password_changed_at", None)
        if changed_at is None:
            return user, token

        token_pwd_changed_at = token.get("pwd_changed_at")
        if token_pwd_changed_at is not None:
            if token_pwd_changed_at != changed_at.isoformat():
                raise AuthenticationFailed("Token was issued before the last password change.")
            return user, token

        # Legacy tokens created before the password-version claim existed use
        # SimpleJWT's integer-second iat. Keep a one-second compatibility
        # window rather than invalidating a freshly issued token because the
        # database timestamp contains sub-second precision.
        issued_at = token.get("iat")
        if issued_at is None:
            raise AuthenticationFailed("Token is missing its issued-at timestamp.")

        changed_epoch = int(changed_at.timestamp())
        if issued_at < changed_epoch:
            raise AuthenticationFailed("Token was issued before the last password change.")

        return user, token
