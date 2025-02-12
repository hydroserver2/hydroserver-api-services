import pytest
import uuid
from ninja.errors import HttpError
from sta.services import DatastreamService
from sta.schemas import DatastreamPostBody, DatastreamPatchBody, DatastreamGetResponse

datastream_service = DatastreamService()


@pytest.mark.parametrize("user, workspace, thing, length, max_queries", [
    ("owner", None, None, 9, 2),
    ("owner", "6e0deaf2-a92b-421b-9ece-86783265596f", None, 5, 2),
    ("owner", "6e0deaf2-a92b-421b-9ece-86783265596f", "3b7818af-eff7-4149-8517-e5cad9dc22e1", 3, 2),
    ("owner", "b27c51a0-7374-462d-8a53-d97d47176c10", None, 4, 2),
    ("owner", "b27c51a0-7374-462d-8a53-d97d47176c10", "76dadda5-224b-4e1f-8570-e385bd482b2d", 2, 2),
    ("owner", "b27c51a0-7374-462d-8a53-d97d47176c10", "3b7818af-eff7-4149-8517-e5cad9dc22e1", 0, 2),
    ("admin", None, None, 9, 2),
    ("admin", "6e0deaf2-a92b-421b-9ece-86783265596f", None, 5, 2),
    ("admin", "6e0deaf2-a92b-421b-9ece-86783265596f", "3b7818af-eff7-4149-8517-e5cad9dc22e1", 3, 2),
    ("admin", "b27c51a0-7374-462d-8a53-d97d47176c10", None, 4, 2),
    ("admin", "b27c51a0-7374-462d-8a53-d97d47176c10", "76dadda5-224b-4e1f-8570-e385bd482b2d", 2, 2),
    ("admin", "b27c51a0-7374-462d-8a53-d97d47176c10", "3b7818af-eff7-4149-8517-e5cad9dc22e1", 0, 2),
    ("editor", None, None, 9, 2),
    ("editor", "6e0deaf2-a92b-421b-9ece-86783265596f", None, 5, 2),
    ("editor", "6e0deaf2-a92b-421b-9ece-86783265596f", "3b7818af-eff7-4149-8517-e5cad9dc22e1", 3, 2),
    ("editor", "b27c51a0-7374-462d-8a53-d97d47176c10", None, 4, 2),
    ("editor", "b27c51a0-7374-462d-8a53-d97d47176c10", "76dadda5-224b-4e1f-8570-e385bd482b2d", 2, 2),
    ("editor", "b27c51a0-7374-462d-8a53-d97d47176c10", "3b7818af-eff7-4149-8517-e5cad9dc22e1", 0, 2),
    ("viewer", None, None, 9, 2),
    ("viewer", "6e0deaf2-a92b-421b-9ece-86783265596f", None, 5, 2),
    ("viewer", "6e0deaf2-a92b-421b-9ece-86783265596f", "3b7818af-eff7-4149-8517-e5cad9dc22e1", 3, 2),
    ("viewer", "b27c51a0-7374-462d-8a53-d97d47176c10", None, 4, 2),
    ("viewer", "b27c51a0-7374-462d-8a53-d97d47176c10", "76dadda5-224b-4e1f-8570-e385bd482b2d", 2, 2),
    ("viewer", "b27c51a0-7374-462d-8a53-d97d47176c10", "3b7818af-eff7-4149-8517-e5cad9dc22e1", 0, 2),
    ("anonymous", None, None, 2, 2),
    ("anonymous", "6e0deaf2-a92b-421b-9ece-86783265596f", None, 2, 2),
    ("anonymous", "6e0deaf2-a92b-421b-9ece-86783265596f", "3b7818af-eff7-4149-8517-e5cad9dc22e1", 2, 2),
    ("anonymous", "b27c51a0-7374-462d-8a53-d97d47176c10", None, 0, 2),
    ("anonymous", "b27c51a0-7374-462d-8a53-d97d47176c10", "76dadda5-224b-4e1f-8570-e385bd482b2d", 0, 2),
    ("anonymous", "b27c51a0-7374-462d-8a53-d97d47176c10", "3b7818af-eff7-4149-8517-e5cad9dc22e1", 0, 2),
    ("anonymous", "00000000-0000-0000-0000-000000000000", None, 0, 2),
    ("anonymous", None, "00000000-0000-0000-0000-000000000000", 0, 2),
])
def test_list_datastream(django_assert_max_num_queries, get_user, user, workspace, thing, length, max_queries):
    with django_assert_max_num_queries(max_queries):
        datastream_list = datastream_service.list(
            user=get_user(user), workspace_id=uuid.UUID(workspace) if workspace else None,
            thing_id=uuid.UUID(thing) if thing else None
        )
        assert len(datastream_list) == length
        assert (DatastreamGetResponse.from_orm(datastream) for datastream in datastream_list)


@pytest.mark.parametrize("user, datastream, message, error_code", [
    ("owner", "27c70b41-e845-40ea-8cc7-d1b40f89816b", "Public Datastream 1", None),
    ("owner", "9f96957b-ee20-4c7b-bf2b-673a0cda3a04", "Private Datastream 7", None),
    ("admin", "27c70b41-e845-40ea-8cc7-d1b40f89816b", "Public Datastream 1", None),
    ("admin", "9f96957b-ee20-4c7b-bf2b-673a0cda3a04", "Private Datastream 7", None),
    ("editor", "27c70b41-e845-40ea-8cc7-d1b40f89816b", "Public Datastream 1", None),
    ("editor", "9f96957b-ee20-4c7b-bf2b-673a0cda3a04", "Private Datastream 7", None),
    ("viewer", "27c70b41-e845-40ea-8cc7-d1b40f89816b", "Public Datastream 1", None),
    ("viewer", "9f96957b-ee20-4c7b-bf2b-673a0cda3a04", "Private Datastream 7", None),
    ("anonymous", "27c70b41-e845-40ea-8cc7-d1b40f89816b", "Public Datastream 1", None),
    ("anonymous", "e0506cac-3e50-4d0a-814d-7ae0146705b2", "Datastream does not exist", 404),
    ("anonymous", "cad40a75-99ca-4317-b534-0fc7880c905f", "Datastream does not exist", 404),
    ("anonymous", "fcd47d93-4cae-411a-9e1e-26ef473840ed", "Datastream does not exist", 404),
    ("anonymous", "dd1f9293-ce29-4b6a-88e6-d65110d1be65", "Datastream does not exist", 404),
    ("anonymous", "1c9a797e-6fd8-4e99-b1ae-87ab4affc0a2", "Datastream does not exist", 404),
    ("anonymous", "42e08eea-27bb-4ea3-8ced-63acff0f3334", "Datastream does not exist", 404),
    ("anonymous", "9f96957b-ee20-4c7b-bf2b-673a0cda3a04", "Datastream does not exist", 404),
    ("anonymous", "00000000-0000-0000-0000-000000000000", "Datastream does not exist", 404),
])
def test_get_datastream(get_user, user, datastream, message, error_code):
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            datastream_service.get(
                user=get_user(user), uid=uuid.UUID(datastream)
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        datastream_get = datastream_service.get(
            user=get_user(user), uid=uuid.UUID(datastream)
        )
        assert datastream_get.name == message
        # assert DatastreamGetResponse.from_orm(datastream_get)


# @pytest.mark.parametrize("user, workspace, message, error_code", [
#     ("owner", "6e0deaf2-a92b-421b-9ece-86783265596f", None, None),
#     ("owner", "b27c51a0-7374-462d-8a53-d97d47176c10", None, None),
#     ("admin", "6e0deaf2-a92b-421b-9ece-86783265596f", None, None),
#     ("admin", "b27c51a0-7374-462d-8a53-d97d47176c10", None, None),
#     ("editor", "6e0deaf2-a92b-421b-9ece-86783265596f", None, None),
#     ("editor", "b27c51a0-7374-462d-8a53-d97d47176c10", None, None),
#     ("viewer", "6e0deaf2-a92b-421b-9ece-86783265596f", "You do not have permission", 403),
#     ("viewer", "b27c51a0-7374-462d-8a53-d97d47176c10", "You do not have permission", 403),
#     ("anonymous", "6e0deaf2-a92b-421b-9ece-86783265596f", "You do not have permission", 403),
#     ("anonymous", "b27c51a0-7374-462d-8a53-d97d47176c10", "Workspace does not exist", 404),
# ])
# def test_create_datastream(get_user, user, workspace, message, error_code):
#     datastream_data = DatastreamPostBody(
#         name="New", symbol="New", definition="New", datastream_type="New", workspace_id=uuid.UUID(workspace)
#     )
#     if error_code:
#         with pytest.raises(HttpError) as exc_info:
#             datastream_service.create(
#                 user=get_user(user), data=datastream_data
#             )
#         assert exc_info.value.status_code == error_code
#         assert exc_info.value.message.startswith(message)
#     else:
#         datastream_create = datastream_service.create(
#             user=get_user(user), data=datastream_data
#         )
#         assert datastream_create.symbol == datastream_data.symbol
#         assert datastream_create.name == datastream_data.name
#         assert datastream_create.definition == datastream_data.definition
#         assert datastream_create.datastream_type == datastream_data.datastream_type


# @pytest.mark.parametrize("user, datastream, message, error_code", [
#     ("owner", "2ca850fa-ce19-4d8a-9dfd-8d54a261778d", "You do not have permission", 403),
#     ("owner", "fe3799b7-f061-42f2-b012-b569303f8a41", None, None),
#     ("owner", "98a74429-2be2-44c0-8f7f-2df2ca12893d", None, None),
#     ("admin", "2ca850fa-ce19-4d8a-9dfd-8d54a261778d", None, None),
#     ("admin", "fe3799b7-f061-42f2-b012-b569303f8a41", None, None),
#     ("admin", "98a74429-2be2-44c0-8f7f-2df2ca12893d", None, None),
#     ("editor", "2ca850fa-ce19-4d8a-9dfd-8d54a261778d", "You do not have permission", 403),
#     ("editor", "fe3799b7-f061-42f2-b012-b569303f8a41", None, None),
#     ("editor", "98a74429-2be2-44c0-8f7f-2df2ca12893d", None, None),
#     ("viewer", "2ca850fa-ce19-4d8a-9dfd-8d54a261778d", "You do not have permission", 403),
#     ("viewer", "fe3799b7-f061-42f2-b012-b569303f8a41", "You do not have permission", 403),
#     ("viewer", "98a74429-2be2-44c0-8f7f-2df2ca12893d", "You do not have permission", 403),
#     ("anonymous", "2ca850fa-ce19-4d8a-9dfd-8d54a261778d", "You do not have permission", 403),
#     ("anonymous", "fe3799b7-f061-42f2-b012-b569303f8a41", "You do not have permission", 403),
#     ("anonymous", "98a74429-2be2-44c0-8f7f-2df2ca12893d", "Datastream does not exist", 404),
#     ("anonymous", "00000000-0000-0000-0000-000000000000", "Datastream does not exist", 404),
# ])
# def test_edit_datastream(get_user, user, datastream, message, error_code):
#     datastream_data = DatastreamPatchBody(
#         name="New", symbol="New", definition="New", datastream_type="New"
#     )
#     if error_code:
#         with pytest.raises(HttpError) as exc_info:
#             datastream_service.update(
#                 user=get_user(user), uid=uuid.UUID(datastream), data=datastream_data
#             )
#         assert exc_info.value.status_code == error_code
#         assert exc_info.value.message.startswith(message)
#     else:
#         datastream_update = datastream_service.update(
#             user=get_user(user), uid=uuid.UUID(datastream), data=datastream_data
#         )
#         assert datastream_update.definition == datastream_data.definition
#         assert datastream_update.name == datastream_data.name
#         assert datastream_update.symbol == datastream_data.symbol
#         assert datastream_update.datastream_type == datastream_data.datastream_type
# 
# 
# @pytest.mark.parametrize("user, datastream, message, error_code", [
#     ("owner", "2ca850fa-ce19-4d8a-9dfd-8d54a261778d", "You do not have permission", 403),
#     ("owner", "fe3799b7-f061-42f2-b012-b569303f8a41", None, None),
#     ("owner", "98a74429-2be2-44c0-8f7f-2df2ca12893d", None, None),
#     ("admin", "2ca850fa-ce19-4d8a-9dfd-8d54a261778d", None, None),
#     ("admin", "fe3799b7-f061-42f2-b012-b569303f8a41", None, None),
#     ("admin", "98a74429-2be2-44c0-8f7f-2df2ca12893d", None, None),
#     ("editor", "2ca850fa-ce19-4d8a-9dfd-8d54a261778d", "You do not have permission", 403),
#     ("editor", "fe3799b7-f061-42f2-b012-b569303f8a41", None, None),
#     ("editor", "98a74429-2be2-44c0-8f7f-2df2ca12893d", None, None),
#     ("viewer", "2ca850fa-ce19-4d8a-9dfd-8d54a261778d", "You do not have permission", 403),
#     ("viewer", "fe3799b7-f061-42f2-b012-b569303f8a41", "You do not have permission", 403),
#     ("viewer", "98a74429-2be2-44c0-8f7f-2df2ca12893d", "You do not have permission", 403),
#     ("anonymous", "2ca850fa-ce19-4d8a-9dfd-8d54a261778d", "You do not have permission", 403),
#     ("anonymous", "fe3799b7-f061-42f2-b012-b569303f8a41", "You do not have permission", 403),
#     ("anonymous", "98a74429-2be2-44c0-8f7f-2df2ca12893d", "Datastream does not exist", 404),
#     ("anonymous", "00000000-0000-0000-0000-000000000000", "Datastream does not exist", 404),
# ])
# def test_delete_datastream(get_user, user, datastream, message, error_code):
#     if error_code:
#         with pytest.raises(HttpError) as exc_info:
#             datastream_service.delete(
#                 user=get_user(user), uid=uuid.UUID(datastream)
#             )
#         assert exc_info.value.status_code == error_code
#         assert exc_info.value.message.startswith(message)
#     else:
#         datastream_delete = datastream_service.delete(
#             user=get_user(user), uid=uuid.UUID(datastream)
#         )
#         assert datastream_delete == "Datastream deleted"
