# import pytest
# import uuid
# from ninja.errors import HttpError
# from iam.services.utils import ServiceUtils
#
#
# service_utils = ServiceUtils()
#
#
# def test_get_workspace_owned(db, test_user, test_workspace_private):
#     workspace, permissions = service_utils.get_workspace(test_user, test_workspace_private.id)
#
#     assert workspace.name == "Private"
#     assert set(permissions) == {"view", "edit", "delete"}
#
#
# def test_get_workspace_collaborator(db, test_collaborator_viewer, test_workspace_private):
#     workspace, permissions = service_utils.get_workspace(test_collaborator_viewer.user, test_workspace_private.id)
#
#     assert workspace.name == "Private"
#     assert set(permissions) == {"view"}
#
#
# def test_get_public_workspace(db, test_user_limited, test_workspace_public):
#     workspace, permissions = service_utils.get_workspace(test_user_limited, test_workspace_public.id)
#
#     assert workspace.name == "Public"
#     assert set(permissions) == {"view"}
#
#
# def test_get_missing_workspace(db, test_user):
#     with pytest.raises(HttpError) as exc_info:
#         service_utils.get_workspace(test_user, uuid.UUID("55a10f52-efb4-4d17-8c38-12f133d7c458"))
#
#     assert exc_info.value.status_code == 404
#
#
# def test_get_private_workspace(db, test_user_limited, test_workspace_private):
#     with pytest.raises(HttpError) as exc_info:
#         service_utils.get_workspace(test_user_limited, test_workspace_private.id)
#
#     assert exc_info.value.status_code == 404
