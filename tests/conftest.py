import pytest
from django.conf import settings
from django.core.management import call_command


@pytest.fixture(scope='session')
def django_db_setup():
    if settings.DATABASES.get('test'):
        settings.DATABASES['default'] = settings.DATABASES['test']
    # settings.DATABASES['default'] = {
    #     'ENGINE': 'django.db.backends.postgresql_psycopg2',
    #     'NAME': 'hydroserver',
    #     'USER': 'postgres',
    #     'PASSWORD': '',
    #     'HOST': 'localhost',
    #     'PORT': 5432,
    #     'ATOMIC_REQUESTS': False,
    # }


@pytest.fixture(scope='session')
def django_test_db(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command('migrate')
        call_command('configure_timescaledb', no_timescale=True)
        call_command('loaddata', 'test_data.yaml')
