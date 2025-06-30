import pytest
import uuid
from collections import Counter
from ninja.errors import HttpError
from django.http import HttpResponse
from iam.services.role import RoleService
from iam.schemas import RoleGetResponse

role_service = RoleService()


@pytest.mark.parametrize(
    "principal, workspace, params, role_names, max_queries",
    [
        # Test user access
        ("owner", "b27c51a0-7374-462d-8a53-d97d47176c10", {}, ["Editor", "Viewer", "Data Loader", "Private"], 7),
        ("editor", "b27c51a0-7374-462d-8a53-d97d47176c10", {}, ["Editor", "Viewer", "Data Loader", "Private"], 7),
        ("viewer", "b27c51a0-7374-462d-8a53-d97d47176c10", {}, ["Editor", "Viewer", "Data Loader", "Private"], 7),
        ("admin", "b27c51a0-7374-462d-8a53-d97d47176c10", {}, ["Editor", "Viewer", "Data Loader", "Private"], 7),
        ("apikey", "6e0deaf2-a92b-421b-9ece-86783265596f", {}, ["Editor", "Viewer", "Data Loader"], 7),
        ("unaffiliated", "6e0deaf2-a92b-421b-9ece-86783265596f", {}, ["Editor", "Viewer", "Data Loader"], 7),
        ("anonymous", "6e0deaf2-a92b-421b-9ece-86783265596f", {}, ["Editor", "Viewer", "Data Loader"], 7),
        # Test pagination and ordering
        ("owner", "b27c51a0-7374-462d-8a53-d97d47176c10", {"page": 2, "page_size": 1, "ordering": "-name"}, ["Private"], 7),
        # Test filtering
        ("owner", "b27c51a0-7374-462d-8a53-d97d47176c10", {"is_apikey_role": True, "is_user_role": False}, ["Data Loader"], 7),
    ],
)
def test_list_role(
    django_assert_max_num_queries,
    get_principal,
    principal,
    workspace,
    params,
    role_names,
    max_queries
):
    with django_assert_max_num_queries(max_queries):
        http_response = HttpResponse()
        result = role_service.list(
            principal=get_principal(principal),
            workspace_id=uuid.UUID(workspace),
            response=http_response,
            page=params.pop("page", 1),
            page_size=params.pop("page_size", 100),
            ordering=params.pop("ordering", None),
            filtering=params,
        )
        assert Counter(str(role.name) for role in result) == Counter(role_names)
        assert (RoleGetResponse.from_orm(role) for role in result)


@pytest.mark.parametrize(
    "principal, workspace, role, message, error_code",
    [
        (
            "owner",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "60b9d8b1-28d1-4d0d-9bee-4e47219d0118",
            "Private",
            None,
        ),
        (
            "admin",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "60b9d8b1-28d1-4d0d-9bee-4e47219d0118",
            "Private",
            None,
        ),
        (
            "apikey",
            "6e0deaf2-a92b-421b-9ece-86783265596f",
            "2f05f775-5d8a-4778-9942-3d13a64ec7a3",
            "Editor",
            None,
        ),
        (
            "anonymous",
            "6e0deaf2-a92b-421b-9ece-86783265596f",
            "2f05f775-5d8a-4778-9942-3d13a64ec7a3",
            "Editor",
            None,
        ),
        (
            None,
            "6e0deaf2-a92b-421b-9ece-86783265596f",
            "2f05f775-5d8a-4778-9942-3d13a64ec7a3",
            "Editor",
            None,
        ),
        (
            "owner",
            "00000000-0000-0000-0000-000000000000",
            "6e0deaf2-a92b-421b-9ece-86783265596f",
            "Workspace does not exist",
            404,
        ),
        (
            "owner",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "00000000-0000-0000-0000-000000000000",
            "Role does not exist",
            404,
        ),
        (
            "apikey",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "60b9d8b1-28d1-4d0d-9bee-4e47219d0118",
            "Workspace does not exist",
            404,
        ),
        (
            "anonymous",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "60b9d8b1-28d1-4d0d-9bee-4e47219d0118",
            "Workspace does not exist",
            404,
        ),
        (
            None,
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "60b9d8b1-28d1-4d0d-9bee-4e47219d0118",
            "Workspace does not exist",
            404,
        ),
    ],
)
def test_get_role(get_principal, principal, workspace, role, message, error_code):
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            role_service.get(
                principal=get_principal(principal),
                workspace_id=uuid.UUID(workspace),
                uid=uuid.UUID(role),
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        role_get = role_service.get(
            principal=get_principal(principal),
            workspace_id=uuid.UUID(workspace),
            uid=uuid.UUID(role),
        )
        assert role_get.name == message
        assert RoleGetResponse.from_orm(role_get)
