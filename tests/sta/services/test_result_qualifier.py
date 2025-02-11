import pytest
import uuid
from ninja.errors import HttpError
from sta.services import ResultQualifierService
from sta.schemas import ResultQualifierPostBody, ResultQualifierPatchBody

result_qualifier_service = ResultQualifierService()


@pytest.mark.parametrize("user, workspace, length, max_queries", [
    ("owner", None, 3, 2),
    ("owner", "b27c51a0-7374-462d-8a53-d97d47176c10", 1, 2),
    ("owner", "caf4b92e-6914-4449-8c8a-efa5a7fd1826", 0, 2),
    ("admin", None, 3, 2),
    ("admin", "b27c51a0-7374-462d-8a53-d97d47176c10", 1, 2),
    ("admin", "caf4b92e-6914-4449-8c8a-efa5a7fd1826", 0, 2),
    ("editor", None, 3, 2),
    ("editor", "b27c51a0-7374-462d-8a53-d97d47176c10", 1, 2),
    ("viewer", None, 3, 2),
    ("viewer", "b27c51a0-7374-462d-8a53-d97d47176c10", 1, 2),
    ("anonymous", None, 2, 2),
    ("anonymous", "6e0deaf2-a92b-421b-9ece-86783265596f", 1, 2),
    ("anonymous", "b27c51a0-7374-462d-8a53-d97d47176c10", 0, 2),
    ("anonymous", "00000000-0000-0000-0000-000000000000", 0, 2),
])
def test_list_result_qualifier(django_assert_num_queries, get_user, user, workspace, length, max_queries):
    with django_assert_num_queries(max_queries):
        workspace_list = result_qualifier_service.list(
            user=get_user(user), workspace_id=uuid.UUID(workspace) if workspace else None
        )
        assert len(workspace_list) == length


@pytest.mark.parametrize("user, result_qualifier, message, error_code", [
    ("owner", "667b63fb-e7a9-4b10-b6d8-9a4bafdf11bf", "SystemResultQualifier", None),
    ("owner", "c66e9597-f474-4a77-afa0-f2b5a673249e", "PublicResultQualifier", None),
    ("owner", "932dffca-0277-4dc2-8129-cb10212c4185", "PrivateResultQualifier", None),
    ("admin", "667b63fb-e7a9-4b10-b6d8-9a4bafdf11bf", "SystemResultQualifier", None),
    ("admin", "c66e9597-f474-4a77-afa0-f2b5a673249e", "PublicResultQualifier", None),
    ("admin", "932dffca-0277-4dc2-8129-cb10212c4185", "PrivateResultQualifier", None),
    ("editor", "667b63fb-e7a9-4b10-b6d8-9a4bafdf11bf", "SystemResultQualifier", None),
    ("editor", "c66e9597-f474-4a77-afa0-f2b5a673249e", "PublicResultQualifier", None),
    ("editor", "932dffca-0277-4dc2-8129-cb10212c4185", "PrivateResultQualifier", None),
    ("viewer", "667b63fb-e7a9-4b10-b6d8-9a4bafdf11bf", "SystemResultQualifier", None),
    ("viewer", "c66e9597-f474-4a77-afa0-f2b5a673249e", "PublicResultQualifier", None),
    ("viewer", "932dffca-0277-4dc2-8129-cb10212c4185", "PrivateResultQualifier", None),
    ("anonymous", "667b63fb-e7a9-4b10-b6d8-9a4bafdf11bf", "SystemResultQualifier", None),
    ("anonymous", "c66e9597-f474-4a77-afa0-f2b5a673249e", "PublicResultQualifier", None),
    ("anonymous", "932dffca-0277-4dc2-8129-cb10212c4185", "Result qualifier does not exist", 404),
    ("anonymous", "00000000-0000-0000-0000-000000000000", "Result qualifier does not exist", 404),
])
def test_get_result_qualifier(get_user, user, result_qualifier, message, error_code):
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            result_qualifier_service.get(
                user=get_user(user), uid=uuid.UUID(result_qualifier)
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        result_qualifier_get = result_qualifier_service.get(
            user=get_user(user), uid=uuid.UUID(result_qualifier)
        )
        assert result_qualifier_get.code == message


@pytest.mark.parametrize("user, workspace, message, error_code", [
    ("owner", "6e0deaf2-a92b-421b-9ece-86783265596f", None, None),
    ("owner", "b27c51a0-7374-462d-8a53-d97d47176c10", None, None),
    ("admin", "6e0deaf2-a92b-421b-9ece-86783265596f", None, None),
    ("admin", "b27c51a0-7374-462d-8a53-d97d47176c10", None, None),
    ("editor", "6e0deaf2-a92b-421b-9ece-86783265596f", None, None),
    ("editor", "b27c51a0-7374-462d-8a53-d97d47176c10", None, None),
    ("viewer", "6e0deaf2-a92b-421b-9ece-86783265596f", "You do not have permission", 403),
    ("viewer", "b27c51a0-7374-462d-8a53-d97d47176c10", "You do not have permission", 403),
    ("anonymous", "6e0deaf2-a92b-421b-9ece-86783265596f", "You do not have permission", 403),
    ("anonymous", "b27c51a0-7374-462d-8a53-d97d47176c10", "Workspace does not exist", 404),
])
def test_create_result_qualifier(get_user, user, workspace, message, error_code):
    result_qualifier_data = ResultQualifierPostBody(
        code="New", description="New", workspace_id=uuid.UUID(workspace)
    )
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            result_qualifier_service.create(
                user=get_user(user), data=result_qualifier_data
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        result_qualifier_create = result_qualifier_service.create(
            user=get_user(user), data=result_qualifier_data
        )
        assert result_qualifier_create.description == result_qualifier_data.description
        assert result_qualifier_create.code == result_qualifier_data.code
        assert result_qualifier_create.workspace_id == result_qualifier_data.workspace_id


@pytest.mark.parametrize("user, result_qualifier, message, error_code", [
    ("owner", "667b63fb-e7a9-4b10-b6d8-9a4bafdf11bf", "You do not have permission", 403),
    ("owner", "c66e9597-f474-4a77-afa0-f2b5a673249e", None, None),
    ("owner", "932dffca-0277-4dc2-8129-cb10212c4185", None, None),
    ("admin", "667b63fb-e7a9-4b10-b6d8-9a4bafdf11bf", None, None),
    ("admin", "c66e9597-f474-4a77-afa0-f2b5a673249e", None, None),
    ("admin", "932dffca-0277-4dc2-8129-cb10212c4185", None, None),
    ("editor", "667b63fb-e7a9-4b10-b6d8-9a4bafdf11bf", "You do not have permission", 403),
    ("editor", "c66e9597-f474-4a77-afa0-f2b5a673249e", None, None),
    ("editor", "932dffca-0277-4dc2-8129-cb10212c4185", None, None),
    ("viewer", "667b63fb-e7a9-4b10-b6d8-9a4bafdf11bf", "You do not have permission", 403),
    ("viewer", "c66e9597-f474-4a77-afa0-f2b5a673249e", "You do not have permission", 403),
    ("viewer", "932dffca-0277-4dc2-8129-cb10212c4185", "You do not have permission", 403),
    ("anonymous", "667b63fb-e7a9-4b10-b6d8-9a4bafdf11bf", "You do not have permission", 403),
    ("anonymous", "c66e9597-f474-4a77-afa0-f2b5a673249e", "You do not have permission", 403),
    ("anonymous", "932dffca-0277-4dc2-8129-cb10212c4185", "Result qualifier does not exist", 404),
    ("anonymous", "00000000-0000-0000-0000-000000000000", "Result qualifier does not exist", 404),
])
def test_edit_result_qualifier(get_user, user, result_qualifier, message, error_code):
    result_qualifier_data = ResultQualifierPatchBody(
        code="New", description="New"
    )
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            result_qualifier_service.update(
                user=get_user(user), uid=uuid.UUID(result_qualifier), data=result_qualifier_data
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        result_qualifier_update = result_qualifier_service.update(
            user=get_user(user), uid=uuid.UUID(result_qualifier), data=result_qualifier_data
        )
        assert result_qualifier_update.description == result_qualifier_data.description
        assert result_qualifier_update.code == result_qualifier_data.code


@pytest.mark.parametrize("user, result_qualifier, message, error_code", [
    ("owner", "667b63fb-e7a9-4b10-b6d8-9a4bafdf11bf", "You do not have permission", 403),
    ("owner", "c66e9597-f474-4a77-afa0-f2b5a673249e", None, None),
    ("owner", "932dffca-0277-4dc2-8129-cb10212c4185", None, None),
    ("admin", "667b63fb-e7a9-4b10-b6d8-9a4bafdf11bf", None, None),
    ("admin", "c66e9597-f474-4a77-afa0-f2b5a673249e", None, None),
    ("admin", "932dffca-0277-4dc2-8129-cb10212c4185", None, None),
    ("editor", "667b63fb-e7a9-4b10-b6d8-9a4bafdf11bf", "You do not have permission", 403),
    ("editor", "c66e9597-f474-4a77-afa0-f2b5a673249e", None, None),
    ("editor", "932dffca-0277-4dc2-8129-cb10212c4185", None, None),
    ("viewer", "667b63fb-e7a9-4b10-b6d8-9a4bafdf11bf", "You do not have permission", 403),
    ("viewer", "c66e9597-f474-4a77-afa0-f2b5a673249e", "You do not have permission", 403),
    ("viewer", "932dffca-0277-4dc2-8129-cb10212c4185", "You do not have permission", 403),
    ("anonymous", "667b63fb-e7a9-4b10-b6d8-9a4bafdf11bf", "You do not have permission", 403),
    ("anonymous", "c66e9597-f474-4a77-afa0-f2b5a673249e", "You do not have permission", 403),
    ("anonymous", "932dffca-0277-4dc2-8129-cb10212c4185", "Result qualifier does not exist", 404),
    ("anonymous", "00000000-0000-0000-0000-000000000000", "Result qualifier does not exist", 404),
])
def test_delete_result_qualifier(get_user, user, result_qualifier, message, error_code):
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            result_qualifier_service.delete(
                user=get_user(user), uid=uuid.UUID(result_qualifier)
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        result_qualifier_delete = result_qualifier_service.delete(
            user=get_user(user), uid=uuid.UUID(result_qualifier)
        )
        assert result_qualifier_delete == "Result qualifier deleted"
