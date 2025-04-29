import pytest
import uuid
from ninja.errors import HttpError
from iam.services.collaborator import CollaboratorService
from iam.schemas import (
    CollaboratorPostBody,
    CollaboratorDeleteBody,
    CollaboratorGetResponse,
)

collaborator_service = CollaboratorService()


@pytest.mark.parametrize(
    "user, workspace, message, error_code",
    [
        ("owner", "b27c51a0-7374-462d-8a53-d97d47176c10", 2, None),
        ("admin", "b27c51a0-7374-462d-8a53-d97d47176c10", 2, None),
        ("editor", "b27c51a0-7374-462d-8a53-d97d47176c10", 2, None),
        ("viewer", "b27c51a0-7374-462d-8a53-d97d47176c10", 2, None),
        ("anonymous", "6e0deaf2-a92b-421b-9ece-86783265596f", 2, None),
        (
            "anonymous",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "Workspace does not exist",
            404,
        ),
        (None, "6e0deaf2-a92b-421b-9ece-86783265596f", 2, None),
        (
            None,
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "Workspace does not exist",
            404,
        ),
    ],
)
def test_list_collaborator(get_user, user, workspace, message, error_code):
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            collaborator_service.list(
                user=get_user(user), workspace_id=uuid.UUID(workspace)
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        collaborator_list = collaborator_service.list(
            user=get_user(user), workspace_id=uuid.UUID(workspace)
        )
        assert len(collaborator_list) == message
        assert (
            CollaboratorGetResponse.from_orm(collaborator)
            for collaborator in collaborator_list
        )


@pytest.mark.parametrize(
    "user, collaborator, workspace, role, message, error_code",
    [
        (
            "owner",
            "anonymous",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "2f05f775-5d8a-4778-9942-3d13a64ec7a3",
            None,
            None,
        ),
        (
            "admin",
            "anonymous",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "2f05f775-5d8a-4778-9942-3d13a64ec7a3",
            None,
            None,
        ),
        (
            "owner",
            "anonymous",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "60b9d8b1-28d1-4d0d-9bee-4e47219d0118",
            None,
            None,
        ),
        (
            "owner",
            "limited",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "2f05f775-5d8a-4778-9942-3d13a64ec7a3",
            None,
            None,
        ),
        (
            "editor",
            "anonymous",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "2f05f775-5d8a-4778-9942-3d13a64ec7a3",
            None,
            None,
        ),
        (
            "viewer",
            "anonymous",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "2f05f775-5d8a-4778-9942-3d13a64ec7a3",
            "You do not have permission",
            403,
        ),
        (
            "anonymous",
            "anonymous",
            "6e0deaf2-a92b-421b-9ece-86783265596f",
            "2f05f775-5d8a-4778-9942-3d13a64ec7a3",
            "You do not have permission",
            403,
        ),
        (
            None,
            "anonymous",
            "6e0deaf2-a92b-421b-9ece-86783265596f",
            "2f05f775-5d8a-4778-9942-3d13a64ec7a3",
            "You do not have permission",
            403,
        ),
        (
            "anonymous",
            "anonymous",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "2f05f775-5d8a-4778-9942-3d13a64ec7a3",
            "Workspace does not exist",
            404,
        ),
        (
            None,
            "anonymous",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "2f05f775-5d8a-4778-9942-3d13a64ec7a3",
            "Workspace does not exist",
            404,
        ),
        (
            "owner",
            "fake",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "2f05f775-5d8a-4778-9942-3d13a64ec7a3",
            "No account with email",
            400,
        ),
        (
            "owner",
            "owner",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "2f05f775-5d8a-4778-9942-3d13a64ec7a3",
            "Account with email",
            400,
        ),
        (
            "owner",
            "viewer",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "2f05f775-5d8a-4778-9942-3d13a64ec7a3",
            "Account with email",
            400,
        ),
        (
            "owner",
            "anonymous",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "00000000-0000-0000-0000-000000000000",
            "Role does not exist",
            404,
        ),
        (
            "owner",
            "anonymous",
            "6e0deaf2-a92b-421b-9ece-86783265596f",
            "60b9d8b1-28d1-4d0d-9bee-4e47219d0118",
            "Role does not exist",
            404,
        ),
    ],
)
def test_create_collaborator(
    get_user, user, collaborator, workspace, role, message, error_code
):
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            collaborator_service.create(
                user=get_user(user),
                workspace_id=uuid.UUID(workspace),
                data=CollaboratorPostBody(
                    email=f"{collaborator}@example.com", role_id=uuid.UUID(role)
                ),
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        collaborator_create = collaborator_service.create(
            user=get_user(user),
            workspace_id=uuid.UUID(workspace),
            data=CollaboratorPostBody(
                email=f"{collaborator}@example.com", role_id=uuid.UUID(role)
            ),
        )
        assert collaborator_create.user.email == f"{collaborator}@example.com"
        assert CollaboratorGetResponse.from_orm(collaborator_create)


@pytest.mark.parametrize(
    "user, collaborator, workspace, role, message, error_code",
    [
        (
            "owner",
            "editor",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "2f05f775-5d8a-4778-9942-3d13a64ec7a3",
            None,
            None,
        ),
        (
            "admin",
            "editor",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "2f05f775-5d8a-4778-9942-3d13a64ec7a3",
            None,
            None,
        ),
        (
            "owner",
            "editor",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "60b9d8b1-28d1-4d0d-9bee-4e47219d0118",
            None,
            None,
        ),
        (
            "editor",
            "viewer",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "2f05f775-5d8a-4778-9942-3d13a64ec7a3",
            None,
            None,
        ),
        (
            "viewer",
            "editor",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "2f05f775-5d8a-4778-9942-3d13a64ec7a3",
            "You do not have permission",
            403,
        ),
        (
            "anonymous",
            "editor",
            "6e0deaf2-a92b-421b-9ece-86783265596f",
            "2f05f775-5d8a-4778-9942-3d13a64ec7a3",
            "You do not have permission",
            403,
        ),
        (
            "anonymous",
            "editor",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "2f05f775-5d8a-4778-9942-3d13a64ec7a3",
            "Workspace does not exist",
            404,
        ),
        (
            None,
            "editor",
            "6e0deaf2-a92b-421b-9ece-86783265596f",
            "2f05f775-5d8a-4778-9942-3d13a64ec7a3",
            "You do not have permission",
            403,
        ),
        (
            None,
            "editor",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "2f05f775-5d8a-4778-9942-3d13a64ec7a3",
            "Workspace does not exist",
            404,
        ),
        (
            "owner",
            "fake",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "2f05f775-5d8a-4778-9942-3d13a64ec7a3",
            "No collaborator with email",
            400,
        ),
        (
            "owner",
            "anonymous",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "2f05f775-5d8a-4778-9942-3d13a64ec7a3",
            "No collaborator with email",
            400,
        ),
        (
            "owner",
            "editor",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "00000000-0000-0000-0000-000000000000",
            "Role does not exist",
            404,
        ),
        (
            "owner",
            "editor",
            "6e0deaf2-a92b-421b-9ece-86783265596f",
            "60b9d8b1-28d1-4d0d-9bee-4e47219d0118",
            "Role does not exist",
            404,
        ),
    ],
)
def test_update_collaborator(
    get_user, user, collaborator, workspace, role, message, error_code
):
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            collaborator_service.update(
                user=get_user(user),
                workspace_id=uuid.UUID(workspace),
                data=CollaboratorPostBody(
                    email=f"{collaborator}@example.com", role_id=uuid.UUID(role)
                ),
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        collaborator_update = collaborator_service.update(
            user=get_user(user),
            workspace_id=uuid.UUID(workspace),
            data=CollaboratorPostBody(
                email=f"{collaborator}@example.com", role_id=uuid.UUID(role)
            ),
        )
        assert collaborator_update.user.email == f"{collaborator}@example.com"
        assert CollaboratorGetResponse.from_orm(collaborator_update)


@pytest.mark.parametrize(
    "user, collaborator, workspace, message, error_code",
    [
        (
            "owner",
            "editor",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "Collaborator removed from workspace",
            None,
        ),
        (
            "admin",
            "editor",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "Collaborator removed from workspace",
            None,
        ),
        (
            "editor",
            "viewer",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "Collaborator removed from workspace",
            None,
        ),
        (
            "viewer",
            "viewer",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "Collaborator removed from workspace",
            None,
        ),
        (
            "viewer",
            "editor",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "You do not have permission",
            403,
        ),
        (
            "anonymous",
            "editor",
            "6e0deaf2-a92b-421b-9ece-86783265596f",
            "You do not have permission",
            403,
        ),
        (
            "anonymous",
            "editor",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "Workspace does not exist",
            404,
        ),
        (
            None,
            "editor",
            "6e0deaf2-a92b-421b-9ece-86783265596f",
            "You do not have permission",
            403,
        ),
        (
            None,
            "editor",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "Workspace does not exist",
            404,
        ),
        (
            "owner",
            "fake",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "No collaborator with email",
            400,
        ),
        (
            "owner",
            "anonymous",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "No collaborator with email",
            400,
        ),
    ],
)
def test_delete_collaborator(
    get_user, user, collaborator, workspace, message, error_code
):
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            collaborator_service.delete(
                user=get_user(user),
                workspace_id=uuid.UUID(workspace),
                data=CollaboratorDeleteBody(email=f"{collaborator}@example.com"),
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        collaborator_delete = collaborator_service.delete(
            user=get_user(user),
            workspace_id=uuid.UUID(workspace),
            data=CollaboratorDeleteBody(email=f"{collaborator}@example.com"),
        )
        assert collaborator_delete == message
