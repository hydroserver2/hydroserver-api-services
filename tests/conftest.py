import pytest
from django.core.management import call_command
from ninja_jwt.tokens import RefreshToken
from accounts.models import Person


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command('migrate')
        call_command('configure_timescaledb', no_timescale=True)

        call_command('loaddata', 'tests/fixtures/organizations.yaml')
        call_command('loaddata', 'tests/fixtures/users.yaml')
        call_command('loaddata', 'tests/fixtures/api_keys.yaml')
        call_command('loaddata', 'tests/fixtures/things.yaml')
        call_command('loaddata', 'tests/fixtures/tags.yaml')
        call_command('loaddata', 'tests/fixtures/units.yaml')
        call_command('loaddata', 'tests/fixtures/processing_levels.yaml')
        call_command('loaddata', 'tests/fixtures/sensors.yaml')
        call_command('loaddata', 'tests/fixtures/observed_properties.yaml')
        call_command('loaddata', 'tests/fixtures/result_qualifiers.yaml')
        call_command('loaddata', 'tests/fixtures/data_loaders.yaml')
        call_command('loaddata', 'tests/fixtures/data_sources.yaml')
        call_command('loaddata', 'tests/fixtures/datastreams.yaml')
        call_command('loaddata', 'tests/fixtures/observations.yaml')


@pytest.fixture(scope='session')
def auth_headers(django_db_setup, django_db_blocker):
    def get_auth_header(username):
        with django_db_blocker.unblock():
            user = Person.objects.get(email=username)
            refresh = RefreshToken.for_user(user)
            return {'HTTP_AUTHORIZATION': 'Bearer ' + str(getattr(refresh, 'access_token'))}

    return {
        'anonymous': {},
        'alice': get_auth_header('alice@example.com'),
        'bob': get_auth_header('bob@example.com'),
        'carol': get_auth_header('carol@example.com'),
        'dave': get_auth_header('539b2e56-9ccf-4a48-8fda-7726fd2a6bea@hydroserver-temp.org'),
        'emily': get_auth_header('emily@example.com')
    }


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass

