import pytest
import uuid
from ninja.errors import HttpError
from sta.services import ProcessingLevelService
from sta.schemas import ProcessingLevelPostBody, ProcessingLevelPatchBody, ProcessingLevelGetResponse

processing_level_service = ProcessingLevelService()


@pytest.mark.parametrize("user, workspace, length, max_queries", [
    ("owner", None, 12, 2),
    ("owner", "b27c51a0-7374-462d-8a53-d97d47176c10", 2, 2),
    ("owner", "caf4b92e-6914-4449-8c8a-efa5a7fd1826", 0, 2),
    ("admin", None, 12, 2),
    ("admin", "b27c51a0-7374-462d-8a53-d97d47176c10", 2, 2),
    ("admin", "caf4b92e-6914-4449-8c8a-efa5a7fd1826", 0, 2),
    ("editor", None, 12, 2),
    ("editor", "b27c51a0-7374-462d-8a53-d97d47176c10", 2, 2),
    ("viewer", None, 12, 2),
    ("viewer", "b27c51a0-7374-462d-8a53-d97d47176c10", 2, 2),
    ("anonymous", None, 10, 2),
    ("anonymous", "6e0deaf2-a92b-421b-9ece-86783265596f", 2, 2),
    ("anonymous", "b27c51a0-7374-462d-8a53-d97d47176c10", 0, 2),
    ("anonymous", "00000000-0000-0000-0000-000000000000", 0, 2),
])
def test_list_processing_level(django_assert_num_queries, get_user, user, workspace, length, max_queries):
    with django_assert_num_queries(max_queries):
        processing_level_list = processing_level_service.list(
            user=get_user(user), workspace_id=uuid.UUID(workspace) if workspace else None
        )
        assert len(processing_level_list) == length
        assert (ProcessingLevelGetResponse.from_orm(processing_level) for processing_level in processing_level_list)


@pytest.mark.parametrize("user, processing_level, message, error_code", [
    ("owner", "1cb782af-6097-4a3f-9988-5fcbfcb5a327", "System Processing Level", None),
    ("owner", "aa2d8fa4-461f-48a4-8bfe-13b6ae6fa575", "Public Processing Level", None),
    ("owner", "fa3c97ce-41b8-4c12-b91a-9127ce0c083a", "Private Processing Level", None),
    ("admin", "1cb782af-6097-4a3f-9988-5fcbfcb5a327", "System Processing Level", None),
    ("admin", "aa2d8fa4-461f-48a4-8bfe-13b6ae6fa575", "Public Processing Level", None),
    ("admin", "fa3c97ce-41b8-4c12-b91a-9127ce0c083a", "Private Processing Level", None),
    ("editor", "1cb782af-6097-4a3f-9988-5fcbfcb5a327", "System Processing Level", None),
    ("editor", "aa2d8fa4-461f-48a4-8bfe-13b6ae6fa575", "Public Processing Level", None),
    ("editor", "fa3c97ce-41b8-4c12-b91a-9127ce0c083a", "Private Processing Level", None),
    ("viewer", "1cb782af-6097-4a3f-9988-5fcbfcb5a327", "System Processing Level", None),
    ("viewer", "aa2d8fa4-461f-48a4-8bfe-13b6ae6fa575", "Public Processing Level", None),
    ("viewer", "fa3c97ce-41b8-4c12-b91a-9127ce0c083a", "Private Processing Level", None),
    ("anonymous", "1cb782af-6097-4a3f-9988-5fcbfcb5a327", "System Processing Level", None),
    ("anonymous", "aa2d8fa4-461f-48a4-8bfe-13b6ae6fa575", "Public Processing Level", None),
    ("anonymous", "fa3c97ce-41b8-4c12-b91a-9127ce0c083a", "Processing level does not exist", 404),
    ("anonymous", "00000000-0000-0000-0000-000000000000", "Processing level does not exist", 404),
])
def test_get_processing_level(get_user, user, processing_level, message, error_code):
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            processing_level_service.get(
                user=get_user(user), uid=uuid.UUID(processing_level)
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        processing_level_get = processing_level_service.get(
            user=get_user(user), uid=uuid.UUID(processing_level)
        )
        assert processing_level_get.code == message
        assert ProcessingLevelGetResponse.from_orm(processing_level_get)


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
def test_create_processing_level(get_user, user, workspace, message, error_code):
    processing_level_data = ProcessingLevelPostBody(
        code="New", definition="New", workspace_id=uuid.UUID(workspace)
    )
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            processing_level_service.create(
                user=get_user(user), data=processing_level_data
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        processing_level_create = processing_level_service.create(
            user=get_user(user), data=processing_level_data
        )
        assert processing_level_create.definition == processing_level_data.definition
        assert processing_level_create.code == processing_level_data.code
        assert processing_level_create.workspace_id == processing_level_data.workspace_id
        assert ProcessingLevelGetResponse.from_orm(processing_level_create)


@pytest.mark.parametrize("user, processing_level, message, error_code", [
    ("owner", "1cb782af-6097-4a3f-9988-5fcbfcb5a327", "You do not have permission", 403),
    ("owner", "aa2d8fa4-461f-48a4-8bfe-13b6ae6fa575", None, None),
    ("owner", "fa3c97ce-41b8-4c12-b91a-9127ce0c083a", None, None),
    ("admin", "1cb782af-6097-4a3f-9988-5fcbfcb5a327", None, None),
    ("admin", "aa2d8fa4-461f-48a4-8bfe-13b6ae6fa575", None, None),
    ("admin", "fa3c97ce-41b8-4c12-b91a-9127ce0c083a", None, None),
    ("editor", "1cb782af-6097-4a3f-9988-5fcbfcb5a327", "You do not have permission", 403),
    ("editor", "aa2d8fa4-461f-48a4-8bfe-13b6ae6fa575", None, None),
    ("editor", "fa3c97ce-41b8-4c12-b91a-9127ce0c083a", None, None),
    ("viewer", "1cb782af-6097-4a3f-9988-5fcbfcb5a327", "You do not have permission", 403),
    ("viewer", "aa2d8fa4-461f-48a4-8bfe-13b6ae6fa575", "You do not have permission", 403),
    ("viewer", "fa3c97ce-41b8-4c12-b91a-9127ce0c083a", "You do not have permission", 403),
    ("anonymous", "1cb782af-6097-4a3f-9988-5fcbfcb5a327", "You do not have permission", 403),
    ("anonymous", "aa2d8fa4-461f-48a4-8bfe-13b6ae6fa575", "You do not have permission", 403),
    ("anonymous", "fa3c97ce-41b8-4c12-b91a-9127ce0c083a", "Processing level does not exist", 404),
    ("anonymous", "00000000-0000-0000-0000-000000000000", "Processing level does not exist", 404),
])
def test_edit_processing_level(get_user, user, processing_level, message, error_code):
    processing_level_data = ProcessingLevelPatchBody(
        code="New", definition="New"
    )
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            processing_level_service.update(
                user=get_user(user), uid=uuid.UUID(processing_level), data=processing_level_data
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        processing_level_update = processing_level_service.update(
            user=get_user(user), uid=uuid.UUID(processing_level), data=processing_level_data
        )
        assert processing_level_update.definition == processing_level_data.definition
        assert processing_level_update.code == processing_level_data.code
        assert ProcessingLevelGetResponse.from_orm(processing_level_update)


@pytest.mark.parametrize("user, processing_level, message, error_code", [
    ("owner", "1cb782af-6097-4a3f-9988-5fcbfcb5a327", "You do not have permission", 403),
    ("owner", "aa2d8fa4-461f-48a4-8bfe-13b6ae6fa575", None, None),
    ("owner", "fa3c97ce-41b8-4c12-b91a-9127ce0c083a", None, None),
    ("admin", "1cb782af-6097-4a3f-9988-5fcbfcb5a327", None, None),
    ("admin", "aa2d8fa4-461f-48a4-8bfe-13b6ae6fa575", None, None),
    ("admin", "fa3c97ce-41b8-4c12-b91a-9127ce0c083a", None, None),
    ("admin", "a7ff1528-e485-4def-b325-45330c1c448c", "Processing level in use by one or more datastreams", 409),
    ("editor", "1cb782af-6097-4a3f-9988-5fcbfcb5a327", "You do not have permission", 403),
    ("editor", "aa2d8fa4-461f-48a4-8bfe-13b6ae6fa575", None, None),
    ("editor", "fa3c97ce-41b8-4c12-b91a-9127ce0c083a", None, None),
    ("viewer", "1cb782af-6097-4a3f-9988-5fcbfcb5a327", "You do not have permission", 403),
    ("viewer", "aa2d8fa4-461f-48a4-8bfe-13b6ae6fa575", "You do not have permission", 403),
    ("viewer", "fa3c97ce-41b8-4c12-b91a-9127ce0c083a", "You do not have permission", 403),
    ("anonymous", "1cb782af-6097-4a3f-9988-5fcbfcb5a327", "You do not have permission", 403),
    ("anonymous", "aa2d8fa4-461f-48a4-8bfe-13b6ae6fa575", "You do not have permission", 403),
    ("anonymous", "fa3c97ce-41b8-4c12-b91a-9127ce0c083a", "Processing level does not exist", 404),
    ("anonymous", "00000000-0000-0000-0000-000000000000", "Processing level does not exist", 404),
])
def test_delete_processing_level(get_user, user, processing_level, message, error_code):
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            processing_level_service.delete(
                user=get_user(user), uid=uuid.UUID(processing_level)
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        processing_level_delete = processing_level_service.delete(
            user=get_user(user), uid=uuid.UUID(processing_level)
        )
        assert processing_level_delete == "Processing level deleted"
