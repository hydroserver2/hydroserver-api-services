import pytest
import uuid
from ninja.errors import HttpError
from iam.services.workspace import WorkspaceService
from iam.schemas import WorkspacePostBody, WorkspacePatchBody


workspace_service = WorkspaceService()


def test_list_workspaces(db, test_workspace_public, test_workspace_private, test_user_limited):
    workspaces = workspace_service.list(user=test_user_limited)

    assert len(workspaces) == 1
    assert workspaces[0].name == "Public"

    workspaces = workspace_service.list(user=test_user_limited, associated_only=True)

    assert len(workspaces) == 0


def test_get_workspace(db, test_workspace_public, test_user_limited):
    workspace = workspace_service.get(user=test_user_limited, uid=test_workspace_public.id)

    assert workspace.name == "Public"


def test_create_workspace(db, test_user, test_user_limited):
    workspace_data = WorkspacePostBody(name="New", private=False)
    workspace = workspace_service.create(user=test_user, data=workspace_data)

    assert workspace.name == "New"

    with pytest.raises(HttpError) as exc_info:
        workspace_service.create(user=test_user_limited, data=workspace_data)

    assert exc_info.value.status_code == 403


def test_update_workspace(db, test_workspace_public, test_user, test_collaborator_viewer):
    workspace_data = WorkspacePatchBody(name="Updated", private=False)

    with pytest.raises(HttpError) as exc_info:
        workspace_service.update(user=test_collaborator_viewer.user, uid=test_workspace_public.id, data=workspace_data)

    assert exc_info.value.status_code == 403

    workspace = workspace_service.update(user=test_user, uid=test_workspace_public.id, data=workspace_data)

    assert workspace.name == "Updated"


def test_delete_workspace(db, test_workspace_public, test_user, test_collaborator_viewer):
    with pytest.raises(HttpError) as exc_info:
        workspace_service.delete(user=test_collaborator_viewer.user, uid=test_workspace_public.id)

    assert exc_info.value.status_code == 403

    workspace_service.delete(user=test_user, uid=test_workspace_public.id)

    with pytest.raises(HttpError) as exc_info:
        workspace_service.get(user=test_user, uid=test_workspace_public.id)

    assert exc_info.value.status_code == 404


def test_transfer_workspace(db):
    pass


def test_accept_workspace_transfer(db):
    pass


def test_reject_workspace_transfer(db):
    pass
