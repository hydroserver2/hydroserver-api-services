"""
WSGI config for hydroserver project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hydroserver.settings')

application = get_wsgi_application()

call_command('migrate')
call_command('setup_admin_user')
call_command('setup_observations')
