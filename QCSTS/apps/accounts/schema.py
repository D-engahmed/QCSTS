from drf_spectacular.extensions import OpenApiAuthenticationExtension


class PasswordChangeAwareJWTAuthenticationExtension(OpenApiAuthenticationExtension):
    """
    Teach drf-spectacular that the custom JWT authenticator is still standard
    Bearer/JWT authentication for OpenAPI purposes.
    """

    target_class = "apps.accounts.authentication.PasswordChangeAwareJWTAuthentication"
    name = "bearerAuth"

    def get_security_definition(self, auto_schema):
        return {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
