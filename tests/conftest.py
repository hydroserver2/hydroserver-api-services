import pytest
from django.conf import settings
from django.core.management import call_command
from ninja_jwt.tokens import RefreshToken
from accounts.models import Person


@pytest.fixture(scope='session')
def django_db_setup():
    if settings.DATABASES.get('test'):
        settings.DATABASES['default'] = settings.DATABASES['test']


@pytest.fixture(scope='session')
def django_test_db(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command('migrate')
        call_command('configure_timescaledb', no_timescale=True)
        call_command('loaddata', 'test_data.yaml')


@pytest.fixture(scope='session')
def django_jwt_auth(django_test_db, django_db_blocker):
    with django_db_blocker.unblock():
        user = Person.objects.get(email='paul@example.com')
        refresh = RefreshToken.for_user(user)
        return getattr(refresh, 'access_token')
