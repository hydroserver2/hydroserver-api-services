import pytest
import uuid
from ninja.errors import HttpError
from sta.services import UnitService
from sta.schemas import UnitPostBody, UnitPatchBody, UnitGetResponse

unit_service = UnitService()


@pytest.mark.parametrize("user, workspace, length, max_queries", [
    ("owner", None, 6, 2),
    ("owner", "b27c51a0-7374-462d-8a53-d97d47176c10", 2, 2),
    ("owner", "caf4b92e-6914-4449-8c8a-efa5a7fd1826", 0, 2),
    ("admin", None, 6, 2),
    ("admin", "b27c51a0-7374-462d-8a53-d97d47176c10", 2, 2),
    ("admin", "caf4b92e-6914-4449-8c8a-efa5a7fd1826", 0, 2),
    ("editor", None, 6, 2),
    ("editor", "b27c51a0-7374-462d-8a53-d97d47176c10", 2, 2),
    ("viewer", None, 6, 2),
    ("viewer", "b27c51a0-7374-462d-8a53-d97d47176c10", 2, 2),
    ("anonymous", None, 4, 2),
    ("anonymous", "6e0deaf2-a92b-421b-9ece-86783265596f", 2, 2),
    ("anonymous", "b27c51a0-7374-462d-8a53-d97d47176c10", 0, 2),
    ("anonymous", "00000000-0000-0000-0000-000000000000", 0, 2),
])
def test_list_unit(django_assert_num_queries, get_user, user, workspace, length, max_queries):
    with django_assert_num_queries(max_queries):
        unit_list = unit_service.list(
            user=get_user(user), workspace_id=uuid.UUID(workspace) if workspace else None
        )
        assert len(unit_list) == length
        assert (UnitGetResponse.from_orm(unit) for unit in unit_list)


@pytest.mark.parametrize("user, unit, message, error_code", [
    ("owner", "2ca850fa-ce19-4d8a-9dfd-8d54a261778d", "System Unit", None),
    ("owner", "fe3799b7-f061-42f2-b012-b569303f8a41", "Public Unit", None),
    ("owner", "98a74429-2be2-44c0-8f7f-2df2ca12893d", "Private Unit", None),
    ("admin", "2ca850fa-ce19-4d8a-9dfd-8d54a261778d", "System Unit", None),
    ("admin", "fe3799b7-f061-42f2-b012-b569303f8a41", "Public Unit", None),
    ("admin", "98a74429-2be2-44c0-8f7f-2df2ca12893d", "Private Unit", None),
    ("editor", "2ca850fa-ce19-4d8a-9dfd-8d54a261778d", "System Unit", None),
    ("editor", "fe3799b7-f061-42f2-b012-b569303f8a41", "Public Unit", None),
    ("editor", "98a74429-2be2-44c0-8f7f-2df2ca12893d", "Private Unit", None),
    ("viewer", "2ca850fa-ce19-4d8a-9dfd-8d54a261778d", "System Unit", None),
    ("viewer", "fe3799b7-f061-42f2-b012-b569303f8a41", "Public Unit", None),
    ("viewer", "98a74429-2be2-44c0-8f7f-2df2ca12893d", "Private Unit", None),
    ("anonymous", "2ca850fa-ce19-4d8a-9dfd-8d54a261778d", "System Unit", None),
    ("anonymous", "fe3799b7-f061-42f2-b012-b569303f8a41", "Public Unit", None),
    ("anonymous", "98a74429-2be2-44c0-8f7f-2df2ca12893d", "Unit does not exist", 404),
    ("anonymous", "00000000-0000-0000-0000-000000000000", "Unit does not exist", 404),
])
def test_get_unit(get_user, user, unit, message, error_code):
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            unit_service.get(
                user=get_user(user), uid=uuid.UUID(unit)
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        unit_get = unit_service.get(
            user=get_user(user), uid=uuid.UUID(unit)
        )
        assert unit_get.name == message
        assert UnitGetResponse.from_orm(unit_get)


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
def test_create_unit(get_user, user, workspace, message, error_code):
    unit_data = UnitPostBody(
        name="New", symbol="New", definition="New", unit_type="New", workspace_id=uuid.UUID(workspace)
    )
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            unit_service.create(
                user=get_user(user), data=unit_data
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        unit_create = unit_service.create(
            user=get_user(user), data=unit_data
        )
        assert unit_create.symbol == unit_data.symbol
        assert unit_create.name == unit_data.name
        assert unit_create.definition == unit_data.definition
        assert unit_create.unit_type == unit_data.unit_type
        assert UnitGetResponse.from_orm(unit_create)


@pytest.mark.parametrize("user, unit, message, error_code", [
    ("owner", "2ca850fa-ce19-4d8a-9dfd-8d54a261778d", "You do not have permission", 403),
    ("owner", "fe3799b7-f061-42f2-b012-b569303f8a41", None, None),
    ("owner", "98a74429-2be2-44c0-8f7f-2df2ca12893d", None, None),
    ("admin", "2ca850fa-ce19-4d8a-9dfd-8d54a261778d", None, None),
    ("admin", "fe3799b7-f061-42f2-b012-b569303f8a41", None, None),
    ("admin", "98a74429-2be2-44c0-8f7f-2df2ca12893d", None, None),
    ("editor", "2ca850fa-ce19-4d8a-9dfd-8d54a261778d", "You do not have permission", 403),
    ("editor", "fe3799b7-f061-42f2-b012-b569303f8a41", None, None),
    ("editor", "98a74429-2be2-44c0-8f7f-2df2ca12893d", None, None),
    ("viewer", "2ca850fa-ce19-4d8a-9dfd-8d54a261778d", "You do not have permission", 403),
    ("viewer", "fe3799b7-f061-42f2-b012-b569303f8a41", "You do not have permission", 403),
    ("viewer", "98a74429-2be2-44c0-8f7f-2df2ca12893d", "You do not have permission", 403),
    ("anonymous", "2ca850fa-ce19-4d8a-9dfd-8d54a261778d", "You do not have permission", 403),
    ("anonymous", "fe3799b7-f061-42f2-b012-b569303f8a41", "You do not have permission", 403),
    ("anonymous", "98a74429-2be2-44c0-8f7f-2df2ca12893d", "Unit does not exist", 404),
    ("anonymous", "00000000-0000-0000-0000-000000000000", "Unit does not exist", 404),
])
def test_edit_unit(get_user, user, unit, message, error_code):
    unit_data = UnitPatchBody(
        name="New", symbol="New", definition="New", unit_type="New"
    )
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            unit_service.update(
                user=get_user(user), uid=uuid.UUID(unit), data=unit_data
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        unit_update = unit_service.update(
            user=get_user(user), uid=uuid.UUID(unit), data=unit_data
        )
        assert unit_update.definition == unit_data.definition
        assert unit_update.name == unit_data.name
        assert unit_update.symbol == unit_data.symbol
        assert unit_update.unit_type == unit_data.unit_type
        assert UnitGetResponse.from_orm(unit_update)


@pytest.mark.parametrize("user, unit, message, error_code", [
    ("owner", "2ca850fa-ce19-4d8a-9dfd-8d54a261778d", "You do not have permission", 403),
    ("owner", "fe3799b7-f061-42f2-b012-b569303f8a41", None, None),
    ("owner", "98a74429-2be2-44c0-8f7f-2df2ca12893d", None, None),
    ("admin", "2ca850fa-ce19-4d8a-9dfd-8d54a261778d", None, None),
    ("admin", "fe3799b7-f061-42f2-b012-b569303f8a41", None, None),
    ("admin", "98a74429-2be2-44c0-8f7f-2df2ca12893d", None, None),
    ("admin", "85c4118e-d1cc-4003-bbc5-5c65af802ae0", "Unit in use by one or more datastreams", 409),
    ("editor", "2ca850fa-ce19-4d8a-9dfd-8d54a261778d", "You do not have permission", 403),
    ("editor", "fe3799b7-f061-42f2-b012-b569303f8a41", None, None),
    ("editor", "98a74429-2be2-44c0-8f7f-2df2ca12893d", None, None),
    ("viewer", "2ca850fa-ce19-4d8a-9dfd-8d54a261778d", "You do not have permission", 403),
    ("viewer", "fe3799b7-f061-42f2-b012-b569303f8a41", "You do not have permission", 403),
    ("viewer", "98a74429-2be2-44c0-8f7f-2df2ca12893d", "You do not have permission", 403),
    ("anonymous", "2ca850fa-ce19-4d8a-9dfd-8d54a261778d", "You do not have permission", 403),
    ("anonymous", "fe3799b7-f061-42f2-b012-b569303f8a41", "You do not have permission", 403),
    ("anonymous", "98a74429-2be2-44c0-8f7f-2df2ca12893d", "Unit does not exist", 404),
    ("anonymous", "00000000-0000-0000-0000-000000000000", "Unit does not exist", 404),
])
def test_delete_unit(get_user, user, unit, message, error_code):
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            unit_service.delete(
                user=get_user(user), uid=uuid.UUID(unit)
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        unit_delete = unit_service.delete(
            user=get_user(user), uid=uuid.UUID(unit)
        )
        assert unit_delete == "Unit deleted"
