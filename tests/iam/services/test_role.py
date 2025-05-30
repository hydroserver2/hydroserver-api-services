import pytest
import uuid
from ninja.errors import HttpError
from iam.services.role import RoleService
from iam.schemas import RoleGetResponse

role_service = RoleService()


@pytest.mark.parametrize(
    "principal, workspace, length, message, error_code",
    [
        ("owner", "b27c51a0-7374-462d-8a53-d97d47176c10", 4, None, None),
        ("admin", "b27c51a0-7374-462d-8a53-d97d47176c10", 4, None, None),
        ("editor", "b27c51a0-7374-462d-8a53-d97d47176c10", 4, None, None),
        ("viewer", "b27c51a0-7374-462d-8a53-d97d47176c10", 4, None, None),
        (
            "apikey",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            0,
            "Workspace does not exist",
            404,
        ),
        (
            "anonymous",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            0,
            "Workspace does not exist",
            404,
        ),
        (
            None,
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            0,
            "Workspace does not exist",
            404,
        ),
        ("owner", "6e0deaf2-a92b-421b-9ece-86783265596f", 3, None, None),
        ("admin", "6e0deaf2-a92b-421b-9ece-86783265596f", 3, None, None),
        ("editor", "6e0deaf2-a92b-421b-9ece-86783265596f", 3, None, None),
        ("viewer", "6e0deaf2-a92b-421b-9ece-86783265596f", 3, None, None),
        ("apikey", "6e0deaf2-a92b-421b-9ece-86783265596f", 3, None, None),
        ("anonymous", "6e0deaf2-a92b-421b-9ece-86783265596f", 3, None, None),
        (None, "6e0deaf2-a92b-421b-9ece-86783265596f", 3, None, None),
    ],
)
def test_list_role(get_principal, principal, workspace, length, message, error_code):
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            role_service.list(
                principal=get_principal(principal), workspace_id=uuid.UUID(workspace)
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        role_list = role_service.list(
            principal=get_principal(principal), workspace_id=uuid.UUID(workspace)
        )
        assert len(role_list) == length
        assert (RoleGetResponse.from_orm(role) for role in role_list)


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
