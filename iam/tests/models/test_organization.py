import pytest
from iam.models import Organization


def test_create_organization(db, test_organization_type_standard):
    organization = Organization.objects.create(
        code="ORG456",
        name="New Organization",
        _organization_type=test_organization_type_standard
    )

    assert organization.code == "ORG456"
    assert organization.name == "New Organization"
    assert organization.organization_type == "Standard"


def test_create_organization_without_type(db):
    organization = Organization.objects.create(
        code="ORG789",
        name="No Type Organization"
    )

    assert organization.code == "ORG789"
    assert organization.name == "No Type Organization"
    assert organization.organization_type is None


def test_organization_type_property(db, test_organization, test_organization_type_admin):
    assert test_organization.organization_type == "Standard"

    test_organization.organization_type = "Admin"
    assert test_organization._organization_type.name == "Admin"


def test_organization_type_property_setter_invalid_type(db, test_organization):
    with pytest.raises(ValueError, match="'InvalidType' is not an allowed user type"):
        test_organization.organization_type = "InvalidType"


def test_organization_type_property_setter_none(db, test_organization):
    test_organization.organization_type = None
    assert test_organization._organization_type is None


def test_organization_type_str_representation(db, test_organization_type_standard):
    assert str(test_organization_type_standard) == "Standard"
