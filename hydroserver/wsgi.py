"""
WSGI config for hydroserver project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os

# from django.core.wsgi import get_wsgi_application
from configurations.wsgi import get_wsgi_application
from django.core.management import call_command
from django.db import connection


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hydroserver.settings")
os.environ.setdefault("DJANGO_CONFIGURATION", os.getenv("SERVER_ENVIRONMENT", "Base"))
application = get_wsgi_application()


def is_leader():
    with connection.cursor() as cursor:
        cursor.execute("SELECT pg_try_advisory_lock(%s);", [1])
        return cursor.fetchone()[0]


if is_leader():
    call_command("migrate")
    call_command("setup_admin_user")
    call_command("collectstatic", "--noinput")
