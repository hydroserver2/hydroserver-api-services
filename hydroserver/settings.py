"""
Django settings for hydroserver project.

Generated by 'django-admin startproject' using Django 4.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

import os
import dj_database_url
from pathlib import Path
from pydantic import BaseSettings, PostgresDsn, EmailStr, HttpUrl
from django.contrib.admin.views.decorators import staff_member_required

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


class EnvironmentSettings(BaseSettings):
    """
    Defines Django environment variables.

    The default settings defined here should only be used in development environments and are not suitable for
    production. In production environments, these settings should be defined using environment variables or a .env file
    in the root project directory.
    """

    # TODO Find/create types for other databases. In the meantime, allow str.
    DATABASE_URL: PostgresDsn | str = f'sqlite:///{BASE_DIR}/db.sqlite3'
    CONN_MAX_AGE: int = 600
    SSL_REQUIRED: bool = False
    SECRET_KEY: str = 'django-insecure-zw@4h#ol@0)5fxy=ib6(t&7o4ot9mzvli*d-wd=81kjxqc!5w4'
    DEBUG: bool = True

    class Config:
        env_file = f'{BASE_DIR}.env'
        case_sensitive = True


config = EnvironmentSettings()


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config.DEBUG

ALLOWED_HOSTS = ['127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'sites.apps.SitesConfig',
    'datastores',
    'sensorthings'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'sensorthings.middleware.SensorThingsRouter'
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

os.environ["DATABASE_URL"] = config.DATABASE_URL

DATABASES = {
    'default': dj_database_url.config(
        conn_max_age=config.CONN_MAX_AGE,
        ssl_require=config.SSL_REQUIRED
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


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static'
]

MEDIA_ROOT = os.path.join(BASE_DIR, 'static/images')
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# SensorThings API Settings

ST_VERSION = '1.1'

ST_API = {
    'title': 'HydroServer SensorThings API',
    'version': ST_VERSION,
    'description': '''
        The HydroServer API can be used to create and update monitoring site metadata, and post  
        results data to HydroServer data stores.
    ''',
    'csrf': False,
    'docs_url': f'/v{ST_VERSION}/docs',
    'openapi_url': f'/v{ST_VERSION}/openapi.json',
    #'docs_decorator': staff_member_required
}

ST_CONFORMANCE = [
    'http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel',
    'http://www.opengis.net/spec/iot_sensing/1.1/req/resource-path/resource-path-to-entities',
    'http://www.opengis.net/spec/iot_sensing/1.1/req/request-data',
    'http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/create-entity',
    'http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/link-to-existing-entities',
    'http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/deep-insert',
    'http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/deep-insert-status-code',
    'http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/update-entity',
    'http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/delete-entity',
    'http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/historical-location-auto-creation'
]

ST_CAPABILITIES = [
    {
        'NAME': 'Things',
        'VIEW': 'get_things'
    },
    {
        'NAME': 'Locations',
        'VIEW': 'get_locations'
    },
    {
        'NAME': 'Datastreams',
        'VIEW': 'get_data_streams'
    },
    {
        'NAME': 'Sensors',
        'VIEW': 'get_sensors'
    },
    {
        'NAME': 'Observations',
        'VIEW': 'get_observations'
    },
    {
        'NAME': 'ObservedProperties',
        'VIEW': 'get_observed_properties'
    },
    {
        'NAME': 'FeaturesOfInterest',
        'VIEW': 'get_features_of_interest'
    },
]
