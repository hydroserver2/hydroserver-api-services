import datetime
import os
import socket
import dj_database_url
import dj_email_url
from pathlib import Path
from uuid import UUID
from corsheaders.defaults import default_headers
from decouple import config
from urllib.parse import urlparse


# Build paths inside the project like this: BASE_DIR / "subdir".
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY", default="django-insecure-zw@4h#ol@0)5fxy=ib6(t&7o4ot9mzvli*d-wd=81kjxqc!5w4")

# SECURITY WARNING: don"t run with debug turned on in production!
DEBUG = config("DEBUG", default=True, cast=bool)
DEPLOYMENT_BACKEND = config("DEPLOYMENT_BACKEND", default="local")


# Default Superuser Settings
DEFAULT_SUPERUSER_EMAIL = config('DEFAULT_SUPERUSER_EMAIL', default='admin@hydroserver.org')
DEFAULT_SUPERUSER_PASSWORD = config('DEFAULT_SUPERUSER_PASSWORD', default='pass')

# Deployment Settings

USE_X_FORWARDED_HOST = True
PROXY_BASE_URL = config("PROXY_BASE_URL", "http://localhost")

hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default=urlparse(PROXY_BASE_URL).netloc).split(",") + [local_ip]

CORS_ALLOWED_ORIGINS = [PROXY_BASE_URL]
CSRF_TRUSTED_ORIGINS = [PROXY_BASE_URL]


# Application definition

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "allauth",
    "allauth.account",
    "allauth.headless",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.orcid",
    "allauth.socialaccount.providers.openid_connect",
    "iam.auth.providers.hydroshare",
    "iam.auth.providers.orcidsandbox",
    "iam.auth.providers.utahid",
    "corsheaders",
    "easyaudit",
    "sensorthings",
    "storages",
    "iam.apps.IamConfig",
    "sta.apps.StaConfig",
    "etl.apps.EtlConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "hydroserver.middleware.CloudHealthCheckMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "easyaudit.middleware.easyaudit.EasyAuditMiddleware",
    "sensorthings.middleware.SensorThingsMiddleware",
]

ROOT_URLCONF = "hydroserver.urls"

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

WSGI_APPLICATION = "hydroserver.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

os.environ["DATABASE_URL"] = config("DATABASE_URL", default=f"postgresql://hsdbadmin:admin@localhost:5432/hydroserver")

DATABASES = {
    "default": {
        **dj_database_url.config(
            engine="django.db.backends.postgresql",
            conn_health_checks=config("CONN_HEALTH_CHECKS", default=True, cast=bool),
            ssl_require=config("SSL_REQUIRED", default=False, cast=bool)
        ),
        "OPTIONS": {
            "application_name": "HydroServer",
            "pool": {
                "min_size": config("DB_POOL_MIN_SIZE", default=5, cast=int),
                "max_size": config("DB_POOL_MAX_SIZE", default=10, cast=int),
                "timeout": config("DB_POOL_TIMEOUT", default=60, cast=int),
            }
        }
    }
}


# Site and Session Settings

SITE_ID = 1

SESSION_COOKIE_NAME = "hs_session"
SESSION_COOKIE_AGE = 86400
SESSION_EXPIRE_AT_BROWSER_CLOSE = False


# Account and Access Control Settings

AUTH_USER_MODEL = "iam.User"

ACCOUNT_SIGNUP_ENABLED = config("ACCOUNT_SIGNUP_ENABLED", default=True, cast=bool)
ACCOUNT_OWNERSHIP_ENABLED = config("ACCOUNT_OWNERSHIP_ENABLED", default=True, cast=bool)

ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_SIGNUP_FORM_CLASS = "iam.auth.forms.UserSignupForm"
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https" if DEPLOYMENT_BACKEND != "local" else "http"

ACCOUNT_ADAPTER = "iam.auth.adapters.AccountAdapter"
HEADLESS_ONLY = True

HEADLESS_FRONTEND_URLS = {
    "account_confirm_email":           f"{PROXY_BASE_URL}/verify-email/{{key}}",
    "account_reset_password_from_key": f"{PROXY_BASE_URL}/reset-password/{{key}}",
    "account_reset_password":          f"{PROXY_BASE_URL}/reset-password",
    "account_signup":                  f"{PROXY_BASE_URL}/sign-up",
}


# Social Account Settings

SOCIALACCOUNT_SIGNUP_ONLY = config("SOCIALACCOUNT_SIGNUP_ONLY", default=False, cast=bool)
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
SOCIALACCOUNT_EMAIL_VERIFICATION = "mandatory"
SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_AUTO_SIGNUP = False


# Email Settings

EMAIL_CONFIG = dj_email_url.parse(config("SMTP_URL", default="smtp://127.0.0.1:1025"))

DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="webmaster@localhost")
EMAIL_BACKEND = EMAIL_CONFIG["EMAIL_BACKEND"]
EMAIL_HOST = EMAIL_CONFIG["EMAIL_HOST"]
EMAIL_PORT = EMAIL_CONFIG["EMAIL_PORT"]
EMAIL_HOST_USER = EMAIL_CONFIG["EMAIL_HOST_USER"]
EMAIL_HOST_PASSWORD = EMAIL_CONFIG["EMAIL_HOST_PASSWORD"]
EMAIL_USE_TLS = EMAIL_CONFIG["EMAIL_USE_TLS"]
EMAIL_USE_SSL = EMAIL_CONFIG["EMAIL_USE_SSL"]


# Audit Settings

ENABLE_AUDITS = config("ENABLE_AUDITS", default=False, cast=bool)

DJANGO_EASY_AUDIT_WATCH_MODEL_EVENTS = ENABLE_AUDITS
DJANGO_EASY_AUDIT_WATCH_AUTH_EVENTS = False
DJANGO_EASY_AUDIT_WATCH_REQUEST_EVENTS = False

DJANGO_EASY_AUDIT_ADMIN_SHOW_MODEL_EVENTS = ENABLE_AUDITS
DJANGO_EASY_AUDIT_ADMIN_SHOW_AUTH_EVENTS = False
DJANGO_EASY_AUDIT_ADMIN_SHOW_REQUEST_EVENTS = False

DJANGO_EASY_AUDIT_UNREGISTERED_CLASSES_EXTRA = ["sta.Observation"]


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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


# Storage settings

APP_CLIENT_URL = config("APP_CLIENT_URL", default=PROXY_BASE_URL)
STATIC_URL = "/static/"
MEDIA_URL = "/media/"
SECURE_CROSS_ORIGIN_OPENER_POLICY = None

if DEPLOYMENT_BACKEND == "aws":
    AWS_S3_CUSTOM_DOMAIN = urlparse(PROXY_BASE_URL).hostname
    AWS_CLOUDFRONT_KEY = config("AWS_CLOUDFRONT_KEY", default="").encode("ascii")
    AWS_CLOUDFRONT_KEY_ID = config("AWS_CLOUDFRONT_KEY_ID", default=None)
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3.S3Storage",
            "OPTIONS": {
                "bucket_name": config("MEDIA_BUCKET_NAME", default=None),
                "location": "media",
                "default_acl": "private"
            },
        },
        "staticfiles": {
            "BACKEND": "storages.backends.s3boto3.S3StaticStorage",
            "OPTIONS": {
                "bucket_name": config("STATIC_BUCKET_NAME", default=None),
                "location": "static",
                "default_acl": None
            },
        }
    }
elif DEPLOYMENT_BACKEND == "gcp":
    GS_PROJECT_ID = config("GS_PROJECT_ID", default=None)
    GS_CUSTOM_ENDPOINT = PROXY_BASE_URL
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.gcloud.GoogleCloudStorage",
            "OPTIONS": {
                "bucket_name": config("MEDIA_BUCKET_NAME", default=None),
                "location": "media",
                "default_acl": "publicRead"
            },
        },
        "staticfiles": {
            "BACKEND": "storages.backends.gcloud.GoogleCloudStorage",
            "OPTIONS": {
                "bucket_name": config("STATIC_BUCKET_NAME", default=None),
                "location": "static",
                "default_acl": "publicRead"
            },
        }
    }
else:
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
            "OPTIONS": {"location": "media"}
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
            "OPTIONS": {"location": "static"}
        },
    }


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# SensorThings Configuration

ST_API_PREFIX = "api/sensorthings"
ST_API_ID_QUALIFIER = "'"
ST_API_ID_TYPE = UUID
