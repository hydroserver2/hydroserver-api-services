import datetime
import os
import socket
import dj_database_url
from pathlib import Path
from uuid import UUID
from corsheaders.defaults import default_headers
from decouple import config
from urllib.parse import urlparse


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-zw@4h#ol@0)5fxy=ib6(t&7o4ot9mzvli*d-wd=81kjxqc!5w4')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)
DEPLOYMENT_BACKEND = config('DEPLOYMENT_BACKEND', default='local')
DISABLE_ACCOUNT_CREATION = config('DISABLE_ACCOUNT_CREATION', default=False, cast=bool)

# CORS Settings

CORS_ORIGIN_ALLOW_ALL = True
CORS_URLS_REGEX = r'^/api/.*$'
CORS_ALLOW_HEADERS = list(default_headers)

# Deployment Settings

if DEPLOYMENT_BACKEND == 'aws':
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)  # This is necessary for AWS ELB Health Checks to pass.
    PROXY_BASE_URL = config('PROXY_BASE_URL')
    ALLOWED_HOSTS = config('ALLOWED_HOSTS', default=PROXY_BASE_URL).split(',') + [local_ip]
    CORS_ALLOW_HEADERS += ['Refresh_Authorization']
elif DEPLOYMENT_BACKEND == 'vm':
    PROXY_BASE_URL = config('PROXY_BASE_URL')
    ALLOWED_HOSTS = config('ALLOWED_HOSTS', default=PROXY_BASE_URL).split(',')
else:
    PROXY_BASE_URL = config('PROXY_BASE_URL', 'http://127.0.0.1:3030')
    ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

CSRF_TRUSTED_ORIGINS = [PROXY_BASE_URL]

LOGIN_REDIRECT_URL = 'sites'
LOGOUT_REDIRECT_URL = 'home'

AUTH_USER_MODEL = 'accounts.Person'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'hydroserver.backends.UnverifiedUserBackend'
]

NINJA_JWT = {
    'ACCESS_TOKEN_LIFETIME': datetime.timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': datetime.timedelta(days=1),
}

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'core.apps.CoreConfig',
    'accounts.apps.AccountsConfig',
    'sensorthings',
    'ninja_extra',
    'simple_history',
    'storages'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'sensorthings.middleware.SensorThingsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware'
]

ROOT_URLCONF = 'hydroserver.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'hydroserver.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

os.environ["DATABASE_URL"] = config('DATABASE_URL', default=f'postgresql://admin:pass@timescaledb:5432/tsdb')

DATABASES = {
    'default': dj_database_url.config(
        conn_max_age=config('CONN_MAX_AGE', default=0),
        conn_health_checks=config('CONN_HEALTH_CHECKS', default=True, cast=bool),
        ssl_require=config('SSL_REQUIRED', default=False, cast=bool)
    )
}

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# OAuth Settings

AUTHLIB_OAUTH_CLIENTS = {
    'orcid': {
        'client_id': config('OAUTH_ORCID_CLIENT', default=''),
        'client_secret': config('OAUTH_ORCID_SECRET', default=''),
        'server_metadata_url': 'https://www.orcid.org/.well-known/openid-configuration'
    },
    'google': {
        'client_id': config('OAUTH_GOOGLE_CLIENT', default=''),
        'client_secret': config('OAUTH_GOOGLE_SECRET', default=''),
        'server_metadata_url': 'https://accounts.google.com/.well-known/openid-configuration'
    },
    'hydroshare': {
        'client_id': config('OAUTH_HYDROSHARE_CLIENT', default=''),
        'client_secret': config('OAUTH_HYDROSHARE_SECRET', default=''),
        'api_base_url': 'https://www.hydroshare.org',
        'authorize_url': 'https://www.hydroshare.org/o/authorize/',
        'access_token_url': 'https://www.hydroshare.org/o/token/'
    }
}

APP_CLIENT_URL = config('APP_CLIENT_URL', default=PROXY_BASE_URL)
SECURE_CROSS_ORIGIN_OPENER_POLICY = None


# Email Settings

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = config('EMAIL_HOST', default=None)
EMAIL_PORT = config('EMAIL_PORT', default=None)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default=None)
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default=None)
DEFAULT_FROM_EMAIL = config('ADMIN_EMAIL', default=None)


if DEPLOYMENT_BACKEND == 'aws':
    AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default=None)
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default=None)
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', default=None)
    AWS_S3_CUSTOM_DOMAIN = urlparse(PROXY_BASE_URL).hostname
    STORAGES = {
        'default': {
            'BACKEND': 'storages.backends.s3.S3Storage',
            'OPTIONS': {'location': 'photos'}
        },
        'staticfiles': {
            'BACKEND': 'storages.backends.s3boto3.S3StaticStorage',
            'OPTIONS': {'location': 'static'}
        }
    }
else:
    STORAGES = {
        'default': {
            'BACKEND': 'django.core.files.storage.FileSystemStorage',
            'OPTIONS': {'location': 'photos'}
        },
        'staticfiles': {
            'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
            'OPTIONS': {'location': 'static'}
        },
    }

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = 'staticfiles'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# SensorThings Configuration

ST_API_PREFIX = 'api/sensorthings'
ST_API_ID_QUALIFIER = "'"
ST_API_ID_TYPE = UUID


# # We need to patch Django Ninja's OpenAPISchema "methods" method to create a unique operationId for endpoints
# # that allow multiple methods on the same view function (such as GET and HEAD in this case). Without this patch,
# # our GET and HEAD methods in the Swagger docs will have the same ID and behave inconsistently. This is probably an
# # unintentional bug with the Django Ninja router.api_operation method when using it for multiple HTTP methods.
#
# from ninja.openapi.schema import OpenAPISchema
#
#
# def _methods_patch(self, operations: list) -> DictStrAny:
#     result = {}
#     for op in operations:
#         if op.include_in_schema:
#             operation_details = self.operation_details(op)
#             for method in op.methods:
#                 # Update the operationId of HEAD methods to avoid conflict with corresponding GET methods.
#                 # Original code:
#                 # result[method.lower()] = operation_details
#                 result[method.lower()] = {
#                     **operation_details,
#                     'operationId': operation_details['operationId'] + '_head'
#                     if method.lower() == 'head' else operation_details['operationId']
#                 }
#     return result
#
#
# OpenAPISchema.methods = _methods_patch
