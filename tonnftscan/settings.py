import json
import os
from pathlib import Path
import environ
import google.cloud.logging
from google.cloud.logging_v2.handlers import CloudLoggingHandler, setup_logging

# Build paths inside the project like this: BASE_DIR / 'subdir'.


BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False),
)

environ.Env.read_env(BASE_DIR / ".env")

ENV = env("ENV")

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")

TON_API_KEY = env("TON_API_KEY")
METABASE_EMBED_KEY = env("METABASE_EMBED_KEY")

TELEGRAM_API_TOKEN = env("TELEGRAM_API_TOKEN")
TELEGRAM_TECH_CHAT_ID = env("TELEGRAM_TECH_CHAT_ID")
TELEGRAM_SUPPORT_CHAT_ID = env("TELEGRAM_SUPPORT_CHAT_ID")
FIREBASE_CREDENTIALS = env("FIREBASE_CREDENTIALS")

METABASE_SITE_URL = "http://localhost:8080"

SITE_URL = env("SITE_URL")
TONSEARCH_URL = env("TONSEARCH_URL", default="https://tonsearch.org")


if ENV == "production":
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
            "LOCATION": BASE_DIR / "var/django_cache",
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        }
    }

if ENV == "production":
    CSRF_TRUSTED_ORIGINS = ["https://tonsearch.org"]
    ALLOWED_HOSTS = ["tonsearch.org", "161.35.196.15"]
else:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
    CSRF_TRUSTED_ORIGINS = ["http://localhost:8008", "http://127.0.0.1:8008"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_api_key",
    "djangorestframework_camel_case",
    "corsheaders",
    "django_better_admin_arrayfield",
    "tonnftscan",
    "indicators",
]

if ENV != "test":
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
else:
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "tonnftscan.middleware.GoogleLoggingMiddleware",
]

ROOT_URLCONF = "tonnftscan.urls"

STATIC_URL = "staticfiles/"

STATIC_ROOT = BASE_DIR / "staticfiles"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "tonnftscan.wsgi.application"

DATABASES = {"default": {"CONN_MAX_AGE": 600, **env.db_url("DATABASE_URL")}}

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

REST_FRAMEWORK = {
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_RENDERER_CLASSES": (
        "djangorestframework_camel_case.render.CamelCaseJSONRenderer",
        "djangorestframework_camel_case.render.CamelCaseBrowsableAPIRenderer",
    ),
    "DEFAULT_PARSER_CLASSES": (
        "djangorestframework_camel_case.parser.CamelCaseFormParser",
        "djangorestframework_camel_case.parser.CamelCaseMultiPartParser",
        "djangorestframework_camel_case.parser.CamelCaseJSONParser",
    ),
}

if not DEBUG:
    REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {"anon": "1312/day", "user": "5000/day"}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        }
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
}

LOG_NAME = "Python-Logs"

if ENV not in ("test", "dev"):
    google_logging_client = google.cloud.logging.Client.from_service_account_info(json.loads(FIREBASE_CREDENTIALS))
    logger = google_logging_client.logger(LOG_NAME)
    handler = CloudLoggingHandler(google_logging_client, name="root")
    setup_logging(handler)

    LOGGING["handlers"]["google_cloud"] = {
        "class": "google.cloud.logging.handlers.CloudLoggingHandler",
        "client": google_logging_client,
        "level": "INFO",
    }
    # Everything is OK with the following line
    LOGGING["root"]["handlers"].append("google_cloud")
else:
    logger = None
