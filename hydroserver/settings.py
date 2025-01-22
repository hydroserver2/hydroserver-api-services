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
    # "hydroserver.providers.hydroshare",
    "corsheaders",
    "sensorthings",
    "storages",
    "iam.apps.IamConfig",
    "core.apps.CoreConfig",
    "stapi.apps.SensorthingsConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
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

os.environ["DATABASE_URL"] = config("DATABASE_URL", default=f"postgresql://admin:pass@127.0.0.1:5432/hydroserver")

DATABASES = {
    "default": dj_database_url.config(
        conn_max_age=config("CONN_MAX_AGE", default=0),
        conn_health_checks=config("CONN_HEALTH_CHECKS", default=True, cast=bool),
        ssl_require=config("SSL_REQUIRED", default=False, cast=bool)
    )
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
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_SIGNUP_FORM_CLASS = "iam.auth.forms.UserSignupForm"

ACCOUNT_ADAPTER = "iam.auth.adapters.AccountAdapter"
HEADLESS_ADAPTER = "iam.auth.adapters.HeadlessAdapter"
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

EMAIL_BACKEND = EMAIL_CONFIG["EMAIL_BACKEND"]
EMAIL_HOST = EMAIL_CONFIG["EMAIL_HOST"]
EMAIL_PORT = EMAIL_CONFIG["EMAIL_PORT"]
EMAIL_HOST_USER = EMAIL_CONFIG["EMAIL_HOST_USER"]
EMAIL_HOST_PASSWORD = EMAIL_CONFIG["EMAIL_HOST_PASSWORD"]
EMAIL_USE_TLS = EMAIL_CONFIG["EMAIL_USE_TLS"]
EMAIL_USE_SSL = EMAIL_CONFIG["EMAIL_USE_SSL"]


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
SECURE_CROSS_ORIGIN_OPENER_POLICY = None

if DEPLOYMENT_BACKEND == "aws":
    AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID", default=None)
    AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY", default=None)
    AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME", default=None)
    AWS_S3_CUSTOM_DOMAIN = urlparse(PROXY_BASE_URL).hostname
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3.S3Storage",
            "OPTIONS": {"location": "photos"}
        },
        "staticfiles": {
            "BACKEND": "storages.backends.s3boto3.S3StaticStorage",
            "OPTIONS": {"location": "static"}
        }
    }
else:
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
            "OPTIONS": {"location": "photos"}
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


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = "staticfiles"


# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# SensorThings Configuration

ST_API_PREFIX = "api/sensorthings"
ST_API_ID_QUALIFIER = "\""
ST_API_ID_TYPE = UUID
