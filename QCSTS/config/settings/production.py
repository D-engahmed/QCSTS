from config.settings.base import *

# Production must fail closed on development credentials. A deployment that
# starts with a known placeholder secret is unsafe even if DEBUG is disabled.
if SECRET_KEY.startswith("django-insecure-") or "change-this-in-production" in SECRET_KEY:
    raise RuntimeError("Refusing to start production with a placeholder DJANGO_SECRET_KEY.")

if DEBUG:
    raise RuntimeError("Refusing to start production with DEBUG=True.")

if not ALLOWED_HOSTS or set(ALLOWED_HOSTS) <= {"localhost", "127.0.0.1"}:
    raise RuntimeError("Production ALLOWED_HOSTS must contain the real application host.")

# Never True in production — exposes sensitive information
DEBUG = False

# Only serve over HTTPS
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
