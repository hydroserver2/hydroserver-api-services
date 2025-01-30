import pytest
from allauth.account.models import EmailAddress
from iam.models import User


def test_create_user(db, test_user_type_standard):
    standard_user = User.objects.create_user(
        email="user@example.com",
        password="password123",
        first_name="First",
        last_name="Last",
        _user_type=test_user_type_standard
    )

    assert standard_user.email == "user@example.com"
    assert standard_user.check_password("password123")
    assert standard_user.is_ownership_allowed is True
    assert User.objects.filter(email="user@example.com").exists()


def test_create_superuser(db, test_user_type_admin):
    superuser = User.objects.create_superuser(
        email="admin@example.com",
        password="adminpass123"
    )

    assert superuser.is_superuser is True
    assert superuser.is_staff is True
    assert superuser._user_type == test_user_type_admin
    assert EmailAddress.objects.filter(user=superuser, email=superuser.email).exists()


def test_create_user_without_email(db):
    with pytest.raises(ValueError, match="Users must have an email address"):
        User.objects.create_user(email=None, password="password123")

    assert User.objects.count() == 0


def test_user_type_property(db, test_user, test_user_type_admin):
    assert test_user.user_type == "Standard"

    test_user.user_type = "Admin"
    assert test_user._user_type.name == "Admin"

    with pytest.raises(ValueError, match="'InvalidType' is not an allowed user type"):
        test_user.user_type = "InvalidType"


def test_account_type_property(db, test_user):
    assert test_user.account_type == "standard"

    test_user.is_ownership_allowed = False
    test_user.save()
    assert test_user.account_type == "limited"

    test_user.is_superuser = True
    test_user.save()
    assert test_user.account_type == "admin"


def test_save_sets_username_to_email(db, test_user):
    test_user.email = "newemail@example.com"
    test_user.save()
    assert test_user.username == "newemail@example.com"


def test_user_str_representation(db, test_user):
    assert str(test_user) == "Test User"

    test_user.first_name = ""
    test_user.save()
    assert str(test_user) == "User"
