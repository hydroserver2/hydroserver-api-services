import pytest
import uuid
from ninja.errors import HttpError
from iam.services.utils import ServiceUtils

service_utils = ServiceUtils()


@pytest.mark.parametrize("user, workspace, message, permissions, error_code", [
    ("owner", "b27c51a0-7374-462d-8a53-d97d47176c10", "Private", {"view", "edit", "delete"}, None),
    ("admin", "b27c51a0-7374-462d-8a53-d97d47176c10", "Private", {"view", "edit", "delete"}, None),
    ("editor", "b27c51a0-7374-462d-8a53-d97d47176c10", "Private", {"view"}, None),
    ("viewer", "b27c51a0-7374-462d-8a53-d97d47176c10", "Private", {"view"}, None),
    ("anonymous", "6e0deaf2-a92b-421b-9ece-86783265596f", "Public", {"view"}, None),
    ("anonymous", "caf4b92e-6914-4449-8c8a-efa5a7fd1826", "Transfer", {"view"}, None),
    ("owner", "00000000-0000-0000-0000-000000000000", "Workspace does not exist", {}, 404),
    ("anonymous", "b27c51a0-7374-462d-8a53-d97d47176c10", "Workspace does not exist", {}, 404),
])
def test_get_workspace(get_user, user, workspace, message, permissions, error_code):
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            service_utils.get_workspace(
                user=get_user(user), workspace_id=uuid.UUID(workspace)
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        workspace_get, workspace_permissions = service_utils.get_workspace(
            user=get_user(user), workspace_id=uuid.UUID(workspace)
        )
        assert workspace_get.name == message
        assert set(workspace_permissions) == permissions
