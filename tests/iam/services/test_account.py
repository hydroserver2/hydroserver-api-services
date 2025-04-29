import pytest
from iam.schemas import (
    AccountPostBody,
    AccountPatchBody,
    OrganizationPostBody,
    OrganizationPatchBody,
    AccountGetResponse,
)
from iam.services.account import AccountService

account_service = AccountService()


@pytest.mark.parametrize("user", ["owner", "admin", "limited", "inactive"])
def test_get_account(get_user, user):
    account = account_service.get(user=get_user(user))
    assert account.email.startswith(user)
    assert AccountGetResponse.from_orm(account)


@pytest.mark.parametrize(
    "account_data",
    [
        AccountPostBody(
            email="new@example.com",
            password="test1234!",
            first_name="New",
            last_name="User",
            user_type="Other",
            organization=OrganizationPostBody(
                code="TEST", name="Test Org", organization_type="Other"
            ),
        ),
    ],
)
def test_create_account(account_data):
    account = account_service.create(data=account_data)
    assert account.email == account_data.email
    assert account.first_name == account_data.first_name
    assert account.last_name == account_data.last_name
    assert account.user_type == account_data.user_type
    assert account.organization.name == account_data.organization.name
    assert account.organization.code == account_data.organization.code
    assert AccountGetResponse.from_orm(account)


@pytest.mark.parametrize(
    "user, account_data",
    [
        (
            "owner",
            AccountPatchBody(
                first_name="New",
                last_name="User",
                user_type="Other",
                organization=OrganizationPatchBody(
                    code="TEST", name="Test Org", organization_type="Other"
                ),
            ),
        ),
    ],
)
def test_update_account(get_user, user, account_data):
    account = account_service.update(user=get_user(user), data=account_data)
    assert account.first_name == account_data.first_name
    assert account.last_name == account_data.last_name
    assert account.user_type == account_data.user_type
    assert account.organization.name == account_data.organization.name
    assert account.organization.code == account_data.organization.code
    assert AccountGetResponse.from_orm(account)


@pytest.mark.parametrize(
    "user, max_queries",
    [
        ("owner", 47),
        ("admin", 41),
        ("limited", 41),
    ],
)
def test_delete_account(django_assert_max_num_queries, get_user, user, max_queries):
    with django_assert_max_num_queries(max_queries):
        message = account_service.delete(get_user(user))
        assert message == "User account has been deleted"
