import pytest
from ninja.errors import HttpError
from iam.schemas import AccountPostBody, AccountPatchBody, OrganizationPostBody


def test_account_post_body_save_valid(db, test_user_type_standard, test_organization_type_standard):
    schema = AccountPostBody(
        email="user@example.com",
        password="password123",
        first_name="First",
        last_name="Last",
        user_type="Standard",
        organization=OrganizationPostBody(
            code="ORG001",
            name="Organization One",
            organization_type="Standard"
        )
    )

    user = schema.save()

    assert user.email == "user@example.com"
    assert user.organization is not None
    assert user.organization.name == "Organization One"


def test_account_post_body_save_invalid_user_type(db):
    schema = AccountPostBody(
        email="user@example.com",
        password="password123",
        first_name="First",
        last_name="Last",
        user_type="InvalidType",
        organization=None
    )

    with pytest.raises(HttpError, match= "'InvalidType' is not an allowed user type."):
        schema.save()


def test_account_patch_body_save_update_user(db, test_user, test_organization):
    schema = AccountPatchBody(  # noqa
        first_name="UpdatedName",
        organization={
            "name": "Updated Organization",
            "link": "https://example.com"
        }
    )  # noqa

    updated_user = schema.save(test_user)

    assert updated_user.first_name == "UpdatedName"
    assert updated_user.organization.name == "Updated Organization"
    assert updated_user.organization.link == "https://example.com"


def test_account_patch_body_save_add_organization(db, test_user):
    schema = AccountPatchBody(  # noqa
        organization={
            "name": "New Organization",
            "link": "https://neworg.com"
        }
    )  # noqa

    updated_user = schema.save(test_user)

    assert updated_user.organization is not None
    assert updated_user.organization.name == "New Organization"
    assert updated_user.organization.link == "https://neworg.com"
