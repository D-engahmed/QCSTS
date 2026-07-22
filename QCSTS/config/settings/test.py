from config.settings.base import *

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
