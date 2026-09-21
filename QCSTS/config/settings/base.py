from pathlib import Path
from datetime import timedelta

import environ


# =============================================================================
# BASE
# =============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")


# =============================================================================
# CORE DJANGO SETTINGS
# =============================================================================

SECRET_KEY = env("DJANGO_SECRET_KEY")

# Paymob webhook HMAC secret. Never commit a real value.
PAYMOB_HMAC_SECRET = env("PAYMOB_HMAC_SECRET", default="")

DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = env.list(
    "ALLOWED_HOSTS",
    default=[
        "localhost",
        "127.0.0.1",
    ],
)


# =============================================================================
# APPLICATIONS
# =============================================================================

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "drf_spectacular",
]

LOCAL_APPS = [
    "core",
    "constants",
    "apps.platform",
    "apps.accounts",
    "apps.audit",
    "apps.billing",
    "apps.products",
    "apps.batches",
    "apps.stability",
    "apps.schedule",
    "apps.results",
    "apps.chamber",
    "apps.reports",
    "apps.quality",
    "apps.compliance",
    "apps.notifications",
]

INSTALLED_APPS = (
    DJANGO_APPS
    + THIRD_PARTY_APPS
    + LOCAL_APPS
)


# =============================================================================
# MIDDLEWARE
# =============================================================================

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# =============================================================================
# URL / WSGI
# =============================================================================

ROOT_URLCONF = "config.urls"

WSGI_APPLICATION = "config.wsgi.application"


# =============================================================================
# TEMPLATES
# =============================================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# =============================================================================
# DATABASE
# =============================================================================
#
# IMPORTANT:
#
# Docker PostgreSQL currently contains:
#
#     cqsts_db
#
# Therefore .env must contain:
#
#     DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:5432/cqsts_db
#
# NOT:
#
#     DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:5432/qcsts_db
#
# =============================================================================

DATABASE_URL = env(
    "DATABASE_URL",
    default="postgresql://postgres:postgres@127.0.0.1:5432/cqsts_db",
)

DATABASES = {
    "default": env.db_url_config(DATABASE_URL),
}


# =============================================================================
# AUTHENTICATION
# =============================================================================

AUTH_USER_MODEL = "accounts.CustomUser"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
        "OPTIONS": {
            "min_length": 12,
        },
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


# =============================================================================
# INTERNATIONALIZATION
# =============================================================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# =============================================================================
# STATIC FILES
# =============================================================================

STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# =============================================================================
# DJANGO REST FRAMEWORK
# =============================================================================

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_SCHEMA_CLASS": (
        "drf_spectacular.openapi.AutoSchema"
    ),
    "EXCEPTION_HANDLER": (
        "core.exceptions.qcsts_exception_handler"
    ),
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.ScopedRateThrottle",
        "rest_framework.throttling.AnonRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "login": env(
            "THROTTLE_LOGIN",
            default="10/min",
        ),
        "signature": env(
            "THROTTLE_SIGNATURE",
            default="20/min",
        ),
        "anon": env(
            "THROTTLE_ANON",
            default="60/min",
        ),
    },
}


# =============================================================================
# JWT
# =============================================================================

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(hours=8),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}


# =============================================================================
# REDIS / CACHE
# =============================================================================

REDIS_URL = env(
    "REDIS_URL",
    default="",
)

if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {
                "CLIENT_CLASS": (
                    "django_redis.client.DefaultClient"
                ),
            },
        },
    }
else:
    CACHES = {
        "default": {
            "BACKEND": (
                "django.core.cache.backends.locmem.LocMemCache"
            ),
            "LOCATION": "qcsts-local-cache",
        },
    }


# =============================================================================
# CELERY
# =============================================================================

CELERY_BROKER_URL = env(
    "CELERY_BROKER_URL",
    default=REDIS_URL or "redis://127.0.0.1:6379/0",
)

CELERY_RESULT_BACKEND = env(
    "CELERY_RESULT_BACKEND",
    default=REDIS_URL or "redis://127.0.0.1:6379/0",
)

CELERY_TIMEZONE = env(
    "CELERY_BEAT_TIMEZONE",
    default="UTC",
)


# =============================================================================
# CORS
# =============================================================================

CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=(
        [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
        if DEBUG
        else []
    ),
)

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_ALL_ORIGINS = False

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "x-signature-token",
    "x-organization-id",
    "x-site-id",
]


# =============================================================================
# DRF SPECTACULAR / OPENAPI
# =============================================================================

SPECTACULAR_SETTINGS = {
    "TITLE": "QCSTS API",
    "DESCRIPTION": (
        "QC Stability Tracking System — Backend API"
    ),
    "VERSION": "1.3.0",
}


# =============================================================================
# LOGGING
# =============================================================================

LOG_DIR = BASE_DIR / "logs"

# Ensure the directory exists before Django initializes FileHandler.
LOG_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

LOG_FILE = LOG_DIR / "cqsts.log"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "verbose": {
            "format": (
                "{levelname} {asctime} "
                "{module} {message}"
            ),
            "style": "{",
        },
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },

        "file": {
            "class": "logging.FileHandler",
            "filename": str(LOG_FILE),
            "formatter": "verbose",
        },
    },

    "root": {
        "handlers": [
            "console",
            "file",
        ],
        "level": "INFO",
    },
}