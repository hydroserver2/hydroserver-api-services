import pytest
from django.db import transaction
from django.core.management import call_command
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command("migrate")

        call_command("load_iam_test_data")
        call_command("load_sta_test_data")
        call_command("load_etl_test_data")


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
