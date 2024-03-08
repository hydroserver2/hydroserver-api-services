import pytest
from django.core.management import call_command
from ninja_jwt.tokens import RefreshToken
from accounts.models import Person


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command('migrate')
        call_command('configure_timescaledb', no_timescale=True)

        call_command('loaddata', 'tests/people/paul.yaml')
        call_command('loaddata', 'tests/people/john.yaml')
        call_command('loaddata', 'tests/people/jane.yaml')

        call_command('loaddata', 'tests/miami/thing.yaml')
        call_command('loaddata', 'tests/lake_michigan/thing.yaml')
        call_command('loaddata', 'tests/cheyenne_creek/thing.yaml')

        call_command('loaddata', 'tests/miami/miami_72.yaml')
        call_command('loaddata', 'tests/lake_michigan/lake_michigan_3.yaml')
        call_command('loaddata', 'tests/cheyenne_creek/cheyenne_creek_0.yaml')
        call_command('loaddata', 'tests/cheyenne_creek/cheyenne_creek_6.yaml')


@pytest.fixture(scope='session')
def django_jwt_auth(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        user = Person.objects.get(email='paul@example.com')
        refresh = RefreshToken.for_user(user)
        return getattr(refresh, 'access_token')


@pytest.fixture
def auth_headers(django_jwt_auth):
    return {
        'HTTP_AUTHORIZATION': 'Bearer ' + str(django_jwt_auth)
    }


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass

