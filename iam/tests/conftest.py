import pytest
from iam.models import User, UserType, Organization, OrganizationType


@pytest.fixture
def test_user_type_admin(db):
    return UserType.objects.get_or_create(name="Admin", public=False)[0]


@pytest.fixture
def test_user_type_standard(db):
    return UserType.objects.get_or_create(name="Standard", public=True)[0]


@pytest.fixture
def test_user(db, test_user_type_standard):
    return User.objects.create_user(
        email="test@example.com",
        password="password123",
        first_name="Test",
        last_name="User",
        _user_type=test_user_type_standard
    )


@pytest.fixture
def test_organization_type_standard(db):
    return OrganizationType.objects.create(name="Standard", public=True)


@pytest.fixture
def test_organization_type_admin(db):
    return OrganizationType.objects.create(name="Admin", public=False)


@pytest.fixture
def test_organization(db, test_organization_type_standard):
    return Organization.objects.create(
        code="ORG123",
        name="Test Organization",
        _organization_type=test_organization_type_standard
    )
