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

        issued_at = token.get("iat")
        if issued_at is None:
            raise AuthenticationFailed("Token is missing its issued-at timestamp.")

        issued_dt = datetime.fromtimestamp(issued_at, tz=timezone.utc)
        if issued_dt < changed_at:
            raise AuthenticationFailed("Token was issued before the last password change.")

        return user, token
