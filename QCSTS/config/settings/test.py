from config.settings.base import *\nimport os

# Use fast in-memory SQLite for tests — no PostgreSQL needed
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
