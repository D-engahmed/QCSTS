from config.settings.base import *
import os

# Use PostgreSQL in CI when CI_DATABASE_URL is supplied; keep SQLite for local tests.
CI_DATABASE_URL = os.environ.get("CI_DATABASE_URL")
if CI_DATABASE_URL:
    DATABASES = {"default": env.db_url_config(CI_DATABASE_URL)}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }

# Disable Redis for tests — use local memory cache instead
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Fast password hashing for tests — bcrypt is slow by design
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Celery runs tasks immediately in tests — no worker needed
CELERY_TASK_ALWAYS_EAGER = True

# Throttles are exercised by dedicated tests that override these rates.
# Leaving production rates on would make the rest of the suite order-dependent.
REST_FRAMEWORK = {**REST_FRAMEWORK, "DEFAULT_THROTTLE_RATES": {
    "login": "10000/min", "signature": "10000/min", "anon": "10000/min",
}}

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
FRONTEND_PUBLIC_URL = "http://testserver"

MFA_ENCRYPTION_KEY = "FNO0V6hoFD3uOI4ZhQbR_rV7bBbiEUdZaz0o-jRM7Lg="

PAYMOB_HMAC_SECRET = "test-secret"

SECRET_KEY = "ci-test-signing-key-0123456789abcdef0123456789abcdef"
