import pytest
import uuid
from ninja.errors import HttpError
from iam.services.workspace import WorkspaceService
from iam.schemas import WorkspacePostBody, WorkspacePatchBody, WorkspaceTransferBody

workspace_service = WorkspaceService()


@pytest.mark.parametrize("user, length, associated", [
    ("owner", 3, False),
    ("owner", 3, True),
    ("admin", 3, False),
    ("admin", 0, True),
    ("editor", 2, False),
    ("editor", 2, True),
    ("viewer", 2, False),
    ("viewer", 2, True),
    ("anonymous", 2, False),
    ("anonymous", 1, True),
    ("limited", 1, False),
    ("limited", 0, True),
])
def test_list_workspace(get_user, user, length, associated):
    workspace_list = workspace_service.list(
        user=get_user(user), associated_only=associated
    )
    assert len(workspace_list) == length


@pytest.mark.parametrize("user, workspace, message, error_code", [
    ("owner", "b27c51a0-7374-462d-8a53-d97d47176c10", "Private", None),
    ("admin", "b27c51a0-7374-462d-8a53-d97d47176c10", "Private", None),
    ("anonymous", "6e0deaf2-a92b-421b-9ece-86783265596f", "Public", None),
    ("anonymous", "caf4b92e-6914-4449-8c8a-efa5a7fd1826", "Transfer", None),
    ("owner", "00000000-0000-0000-0000-000000000000", "Workspace does not exist", 404),
    ("anonymous", "b27c51a0-7374-462d-8a53-d97d47176c10", "Workspace does not exist", 404),
])
def test_get_workspace(get_user, user, workspace, message, error_code):
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            workspace_service.get(
                user=get_user(user), uid=uuid.UUID(workspace)
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        workspace_get = workspace_service.get(
            user=get_user(user), uid=uuid.UUID(workspace)
        )
        assert workspace_get.name == message


@pytest.mark.parametrize("user, message, error_code", [
    ("owner", "New", None),
    ("admin", "New", None),
    ("limited", "You do not have permission to create this workspace", 403),
])
def test_create_workspace(get_user, user, message, error_code):
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            workspace_service.create(
                user=get_user(user), data=WorkspacePostBody(name="New", is_private=False)
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        workspace_update = workspace_service.create(
            user=get_user(user), data=WorkspacePostBody(name="New", is_private=False)
        )
        assert workspace_update.name == message


@pytest.mark.parametrize("user, workspace, message, error_code", [
    ("owner", "6e0deaf2-a92b-421b-9ece-86783265596f", "Updated", None),
    ("admin", "6e0deaf2-a92b-421b-9ece-86783265596f", "Updated", None),
    ("owner", "00000000-0000-0000-0000-000000000000", "Workspace does not exist", 404),
    ("anonymous", "b27c51a0-7374-462d-8a53-d97d47176c10", "Workspace does not exist", 404),
    ("anonymous", "6e0deaf2-a92b-421b-9ece-86783265596f", "You do not have permission to edit this workspace", 403),
])
def test_update_workspace(get_user, user, workspace, message, error_code):
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            workspace_service.update(
                user=get_user(user), uid=uuid.UUID(workspace), data=WorkspacePatchBody(name="Updated", is_private=False)
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        workspace_update = workspace_service.update(
            user=get_user(user), uid=uuid.UUID(workspace), data=WorkspacePatchBody(name="Updated", is_private=False)
        )
        assert workspace_update.name == message


@pytest.mark.parametrize("user, workspace, message, error_code, max_queries", [
    ("owner", "6e0deaf2-a92b-421b-9ece-86783265596f", "Workspace deleted", None, 20),
    ("admin", "6e0deaf2-a92b-421b-9ece-86783265596f", "Workspace deleted", None, 20),
    ("owner", "00000000-0000-0000-0000-000000000000", "Workspace does not exist", 404, 2),
    ("anonymous", "b27c51a0-7374-462d-8a53-d97d47176c10", "Workspace does not exist", 404, 5),
    ("editor", "6e0deaf2-a92b-421b-9ece-86783265596f", "You do not have permission to delete this workspace", 403, 3),
])
def test_delete_workspace(django_assert_max_num_queries, get_user, user, workspace, message, error_code, max_queries):
    with django_assert_max_num_queries(max_queries):
        if error_code:
            with pytest.raises(HttpError) as exc_info:
                workspace_service.delete(
                    user=get_user(user), uid=uuid.UUID(workspace)
                )
            assert exc_info.value.status_code == error_code
            assert exc_info.value.message.startswith(message)
        else:
            workspace_delete = workspace_service.delete(
                user=get_user(user), uid=uuid.UUID(workspace)
            )
            assert workspace_delete == message


@pytest.mark.parametrize("from_user, to_user, workspace, message, error_code", [
    ("owner", "anonymous", "6e0deaf2-a92b-421b-9ece-86783265596f", "Workspace transfer initiated", None),
    ("admin", "anonymous", "6e0deaf2-a92b-421b-9ece-86783265596f", "Workspace transfer initiated", None),
    ("owner", "anonymous", "00000000-0000-0000-0000-000000000000", "Workspace does not exist", 404),
    ("anonymous", "viewer", "b27c51a0-7374-462d-8a53-d97d47176c10", "Workspace does not exist", 404),
    ("editor", "viewer", "6e0deaf2-a92b-421b-9ece-86783265596f", "You do not have permission to transfer", 403),
    ("owner", "fake", "6e0deaf2-a92b-421b-9ece-86783265596f", "No account with email", 400),
    ("owner", "limited", "6e0deaf2-a92b-421b-9ece-86783265596f", "Workspace cannot be transferred to user", 400),
    ("owner", "owner", "6e0deaf2-a92b-421b-9ece-86783265596f", "Workspace already owned by user", 400),
    ("owner", "anonymous", "caf4b92e-6914-4449-8c8a-efa5a7fd1826", "Workspace transfer is already pending", 400),
])
def test_transfer_workspace(get_user, from_user, to_user, workspace, message, error_code):
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            workspace_service.transfer(
                user=get_user(from_user), uid=uuid.UUID(workspace),
                data=WorkspaceTransferBody(new_owner=getattr(get_user(to_user), "email", "fake@example.com")),
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        workspace_transfer = workspace_service.transfer(
            user=get_user(from_user), uid=uuid.UUID(workspace),
            data=WorkspaceTransferBody(new_owner=get_user(to_user).email),
        )
        assert workspace_transfer == message


@pytest.mark.parametrize("user, workspace, message, error_code", [
    ("anonymous", "caf4b92e-6914-4449-8c8a-efa5a7fd1826", "Workspace transfer accepted", None),
    ("anonymous", "b27c51a0-7374-462d-8a53-d97d47176c10", "Workspace does not exist", 404),
    ("owner", "b27c51a0-7374-462d-8a53-d97d47176c10", "No workspace transfer is pending", 400),
    ("owner", "caf4b92e-6914-4449-8c8a-efa5a7fd1826", "You do not have permission to accept", 403),
])
def test_accept_workspace_transfer(get_user, user, workspace, message, error_code):
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            workspace_service.accept_transfer(
                user=get_user(user), uid=uuid.UUID(workspace)
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        workspace_transfer = workspace_service.accept_transfer(
            user=get_user(user), uid=uuid.UUID(workspace)
        )
        workspace_get = workspace_service.get(
            user=get_user(user), uid=uuid.UUID(workspace)
        )
        assert workspace_transfer == message
        assert workspace_get.owner == get_user(user)


@pytest.mark.parametrize("user, workspace, message, error_code", [
    ("anonymous", "caf4b92e-6914-4449-8c8a-efa5a7fd1826", "Workspace transfer rejected", None),
    ("owner", "caf4b92e-6914-4449-8c8a-efa5a7fd1826", "Workspace transfer rejected", None),
    ("anonymous", "b27c51a0-7374-462d-8a53-d97d47176c10", "Workspace does not exist", 404),
    ("owner", "b27c51a0-7374-462d-8a53-d97d47176c10", "No workspace transfer is pending", 400),
])
def test_reject_workspace_transfer(get_user, user, workspace, message, error_code):
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            workspace_service.reject_transfer(
                user=get_user(user), uid=uuid.UUID(workspace)
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        workspace_transfer = workspace_service.reject_transfer(
            user=get_user(user), uid=uuid.UUID(workspace)
        )
        assert workspace_transfer == message
