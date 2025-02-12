import pytest
from django.db import transaction
from django.core.management import call_command
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command("migrate")

        call_command("loaddata", "tests/fixtures/test_users.yaml")
        call_command("loaddata", "tests/fixtures/test_workspaces.yaml")
        call_command("loaddata", "tests/fixtures/test_roles.yaml")
        call_command("loaddata", "tests/fixtures/test_collaborators.yaml")
        call_command("loaddata", "tests/fixtures/test_things.yaml")
        call_command("loaddata", "tests/fixtures/test_observed_properties.yaml")
        call_command("loaddata", "tests/fixtures/test_processing_levels.yaml")
        call_command("loaddata", "tests/fixtures/test_result_qualifiers.yaml")
        call_command("loaddata", "tests/fixtures/test_sensors.yaml")
        call_command("loaddata", "tests/fixtures/test_units.yaml")
        call_command("loaddata", "tests/fixtures/test_datastreams.yaml")


@pytest.fixture(scope="function")
def transactional_db(django_db_setup, db):
    with transaction.atomic():
        yield
        transaction.set_rollback(True)


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture
def get_user():
    def _get_user(email):
        try:
            return User.objects.get(email=f"{email}@example.com")
        except User.DoesNotExist:
            return None
    return _get_user
