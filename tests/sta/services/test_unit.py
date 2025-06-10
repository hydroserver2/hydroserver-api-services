import pytest
import uuid
from collections import Counter
from ninja.errors import HttpError
from django.http import HttpResponse
from sta.services import UnitService
from sta.schemas import UnitPostBody, UnitPatchBody, UnitGetResponse

unit_service = UnitService()


@pytest.mark.parametrize(
    "principal, params, unit_ids, max_queries",
    [
        (
            "owner",
            {},
            [
                "2ca850fa-ce19-4d8a-9dfd-8d54a261778d",
                "383f9663-6003-4baf-b606-7e9937b96298",
                "fe3799b7-f061-42f2-b012-b569303f8a41",
                "85c4118e-d1cc-4003-bbc5-5c65af802ae0",
                "98a74429-2be2-44c0-8f7f-2df2ca12893d",
                "3264c5f7-ccad-4e5b-b7a0-faf175be4750",
            ],
            3,
        ),
        (
            "owner",
            {"workspace_id": "b27c51a0-7374-462d-8a53-d97d47176c10"},
            [
                "98a74429-2be2-44c0-8f7f-2df2ca12893d",
                "3264c5f7-ccad-4e5b-b7a0-faf175be4750",
            ],
            3,
        ),
        ("owner", {"workspace_id": "caf4b92e-6914-4449-8c8a-efa5a7fd1826"}, [], 3),
        (
            "owner",
            {"page": 2, "page_size": 1, "ordering": "-name"},
            [
                "2ca850fa-ce19-4d8a-9dfd-8d54a261778d",
                "383f9663-6003-4baf-b606-7e9937b96298",
            ],
            6,
        ),
        (
            "admin",
            {},
            [
                "2ca850fa-ce19-4d8a-9dfd-8d54a261778d",
                "383f9663-6003-4baf-b606-7e9937b96298",
                "fe3799b7-f061-42f2-b012-b569303f8a41",
                "85c4118e-d1cc-4003-bbc5-5c65af802ae0",
                "98a74429-2be2-44c0-8f7f-2df2ca12893d",
                "3264c5f7-ccad-4e5b-b7a0-faf175be4750",
            ],
            3,
        ),
        (
            "admin",
            {"workspace_id": "b27c51a0-7374-462d-8a53-d97d47176c10"},
            [
                "98a74429-2be2-44c0-8f7f-2df2ca12893d",
                "3264c5f7-ccad-4e5b-b7a0-faf175be4750",
            ],
            3,
        ),
        ("admin", {"workspace_id": "caf4b92e-6914-4449-8c8a-efa5a7fd1826"}, [], 3),
        (
            "editor",
            {},
            [
                "2ca850fa-ce19-4d8a-9dfd-8d54a261778d",
                "383f9663-6003-4baf-b606-7e9937b96298",
                "fe3799b7-f061-42f2-b012-b569303f8a41",
                "85c4118e-d1cc-4003-bbc5-5c65af802ae0",
                "98a74429-2be2-44c0-8f7f-2df2ca12893d",
                "3264c5f7-ccad-4e5b-b7a0-faf175be4750",
            ],
            3,
        ),
        (
            "editor",
            {"workspace_id": "b27c51a0-7374-462d-8a53-d97d47176c10"},
            [
                "98a74429-2be2-44c0-8f7f-2df2ca12893d",
                "3264c5f7-ccad-4e5b-b7a0-faf175be4750",
            ],
            3,
        ),
        (
            "viewer",
            {},
            [
                "2ca850fa-ce19-4d8a-9dfd-8d54a261778d",
                "383f9663-6003-4baf-b606-7e9937b96298",
                "fe3799b7-f061-42f2-b012-b569303f8a41",
                "85c4118e-d1cc-4003-bbc5-5c65af802ae0",
                "98a74429-2be2-44c0-8f7f-2df2ca12893d",
                "3264c5f7-ccad-4e5b-b7a0-faf175be4750",
            ],
            3,
        ),
        (
            "viewer",
            {"workspace_id": "b27c51a0-7374-462d-8a53-d97d47176c10"},
            [
                "98a74429-2be2-44c0-8f7f-2df2ca12893d",
                "3264c5f7-ccad-4e5b-b7a0-faf175be4750",
            ],
            3,
        ),
        (
            "apikey",
            {},
            [
                "2ca850fa-ce19-4d8a-9dfd-8d54a261778d",
                "383f9663-6003-4baf-b606-7e9937b96298",
                "fe3799b7-f061-42f2-b012-b569303f8a41",
                "85c4118e-d1cc-4003-bbc5-5c65af802ae0",
            ],
            4,
        ),
        (
            "apikey",
            {"workspace_id": "6e0deaf2-a92b-421b-9ece-86783265596f"},
            [
                "fe3799b7-f061-42f2-b012-b569303f8a41",
                "85c4118e-d1cc-4003-bbc5-5c65af802ae0",
            ],
            4,
        ),
        ("apikey", {"workspace_id": "b27c51a0-7374-462d-8a53-d97d47176c10"}, [], 4),
        (
            "anonymous",
            {},
            [
                "2ca850fa-ce19-4d8a-9dfd-8d54a261778d",
                "383f9663-6003-4baf-b606-7e9937b96298",
                "fe3799b7-f061-42f2-b012-b569303f8a41",
                "85c4118e-d1cc-4003-bbc5-5c65af802ae0",
            ],
            3,
        ),
        (
            "anonymous",
            {"workspace_id": "6e0deaf2-a92b-421b-9ece-86783265596f"},
            [
                "fe3799b7-f061-42f2-b012-b569303f8a41",
                "85c4118e-d1cc-4003-bbc5-5c65af802ae0",
            ],
            3,
        ),
        ("anonymous", {"workspace_id": "b27c51a0-7374-462d-8a53-d97d47176c10"}, [], 3),
        ("anonymous", {"workspace_id": "00000000-0000-0000-0000-000000000000"}, [], 3),
        (
            None,
            {},
            [
                "2ca850fa-ce19-4d8a-9dfd-8d54a261778d",
                "383f9663-6003-4baf-b606-7e9937b96298",
                "fe3799b7-f061-42f2-b012-b569303f8a41",
                "85c4118e-d1cc-4003-bbc5-5c65af802ae0",
            ],
            3,
        ),
        (
            None,
            {"workspace_id": "6e0deaf2-a92b-421b-9ece-86783265596f"},
            [
                "fe3799b7-f061-42f2-b012-b569303f8a41",
                "85c4118e-d1cc-4003-bbc5-5c65af802ae0",
            ],
            3,
        ),
        (None, {"workspace_id": "b27c51a0-7374-462d-8a53-d97d47176c10"}, [], 3),
        (None, {"workspace_id": "00000000-0000-0000-0000-000000000000"}, [], 3),
    ],
)
def test_list_unit(
    django_assert_num_queries, get_principal, principal, params, unit_ids, max_queries
):
    with django_assert_num_queries(max_queries):
        http_response = HttpResponse()
        result = unit_service.list(
            principal=get_principal(principal),
            response=http_response,
            page=params.pop("page", 1),
            page_size=params.pop("page_size", 100),
            ordering=params.pop("ordering", None),
            filtering=params,
        )
        assert Counter(str(unit.id) for unit in result) == Counter(unit_ids)
        assert (UnitGetResponse.from_orm(unit) for unit in result)


@pytest.mark.parametrize(
    "principal, unit, message, error_code",
    [
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
        ("apikey", "2ca850fa-ce19-4d8a-9dfd-8d54a261778d", "System Unit", None),
        ("apikey", "fe3799b7-f061-42f2-b012-b569303f8a41", "Public Unit", None),
        (
            "apikey",
            "98a74429-2be2-44c0-8f7f-2df2ca12893d",
            "Unit does not exist",
            404,
        ),
        ("anonymous", "2ca850fa-ce19-4d8a-9dfd-8d54a261778d", "System Unit", None),
        ("anonymous", "fe3799b7-f061-42f2-b012-b569303f8a41", "Public Unit", None),
        (
            "anonymous",
            "98a74429-2be2-44c0-8f7f-2df2ca12893d",
            "Unit does not exist",
            404,
        ),
        (
            "anonymous",
            "00000000-0000-0000-0000-000000000000",
            "Unit does not exist",
            404,
        ),
        (None, "2ca850fa-ce19-4d8a-9dfd-8d54a261778d", "System Unit", None),
        (None, "fe3799b7-f061-42f2-b012-b569303f8a41", "Public Unit", None),
        (
            None,
            "98a74429-2be2-44c0-8f7f-2df2ca12893d",
            "Unit does not exist",
            404,
        ),
        (
            None,
            "00000000-0000-0000-0000-000000000000",
            "Unit does not exist",
            404,
        ),
    ],
)
def test_get_unit(get_principal, principal, unit, message, error_code):
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            unit_service.get(principal=get_principal(principal), uid=uuid.UUID(unit))
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        unit_get = unit_service.get(
            principal=get_principal(principal), uid=uuid.UUID(unit)
        )
        assert unit_get.name == message
        assert UnitGetResponse.from_orm(unit_get)


@pytest.mark.parametrize(
    "principal, workspace, message, error_code",
    [
        ("owner", "6e0deaf2-a92b-421b-9ece-86783265596f", None, None),
        ("owner", "b27c51a0-7374-462d-8a53-d97d47176c10", None, None),
        ("admin", "6e0deaf2-a92b-421b-9ece-86783265596f", None, None),
        ("admin", "b27c51a0-7374-462d-8a53-d97d47176c10", None, None),
        ("editor", "6e0deaf2-a92b-421b-9ece-86783265596f", None, None),
        ("editor", "b27c51a0-7374-462d-8a53-d97d47176c10", None, None),
        (
            "viewer",
            "6e0deaf2-a92b-421b-9ece-86783265596f",
            "You do not have permission",
            403,
        ),
        (
            "viewer",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "You do not have permission",
            403,
        ),
        (
            "apikey",
            "6e0deaf2-a92b-421b-9ece-86783265596f",
            "You do not have permission",
            403,
        ),
        (
            "apikey",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "Workspace does not exist",
            404,
        ),
        (
            "anonymous",
            "6e0deaf2-a92b-421b-9ece-86783265596f",
            "You do not have permission",
            403,
        ),
        (
            "anonymous",
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "Workspace does not exist",
            404,
        ),
        (
            None,
            "6e0deaf2-a92b-421b-9ece-86783265596f",
            "You do not have permission",
            403,
        ),
        (
            None,
            "b27c51a0-7374-462d-8a53-d97d47176c10",
            "Workspace does not exist",
            404,
        ),
    ],
)
def test_create_unit(get_principal, principal, workspace, message, error_code):
    unit_data = UnitPostBody(
        name="New",
        symbol="New",
        definition="New",
        unit_type="New",
        workspace_id=uuid.UUID(workspace),
    )
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            unit_service.create(principal=get_principal(principal), data=unit_data)
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        unit_create = unit_service.create(
            principal=get_principal(principal), data=unit_data
        )
        assert unit_create.symbol == unit_data.symbol
        assert unit_create.name == unit_data.name
        assert unit_create.definition == unit_data.definition
        assert unit_create.unit_type == unit_data.unit_type
        assert UnitGetResponse.from_orm(unit_create)


@pytest.mark.parametrize(
    "principal, unit, message, error_code",
    [
        (
            "owner",
            "2ca850fa-ce19-4d8a-9dfd-8d54a261778d",
            "You do not have permission",
            403,
        ),
        ("owner", "fe3799b7-f061-42f2-b012-b569303f8a41", None, None),
        ("owner", "98a74429-2be2-44c0-8f7f-2df2ca12893d", None, None),
        ("admin", "2ca850fa-ce19-4d8a-9dfd-8d54a261778d", None, None),
        ("admin", "fe3799b7-f061-42f2-b012-b569303f8a41", None, None),
        ("admin", "98a74429-2be2-44c0-8f7f-2df2ca12893d", None, None),
        (
            "editor",
            "2ca850fa-ce19-4d8a-9dfd-8d54a261778d",
            "You do not have permission",
            403,
        ),
        ("editor", "fe3799b7-f061-42f2-b012-b569303f8a41", None, None),
        ("editor", "98a74429-2be2-44c0-8f7f-2df2ca12893d", None, None),
        (
            "viewer",
            "2ca850fa-ce19-4d8a-9dfd-8d54a261778d",
            "You do not have permission",
            403,
        ),
        (
            "viewer",
            "fe3799b7-f061-42f2-b012-b569303f8a41",
            "You do not have permission",
            403,
        ),
        (
            "viewer",
            "98a74429-2be2-44c0-8f7f-2df2ca12893d",
            "You do not have permission",
            403,
        ),
        (
            "apikey",
            "2ca850fa-ce19-4d8a-9dfd-8d54a261778d",
            "You do not have permission",
            403,
        ),
        (
            "apikey",
            "fe3799b7-f061-42f2-b012-b569303f8a41",
            "You do not have permission",
            403,
        ),
        (
            "apikey",
            "98a74429-2be2-44c0-8f7f-2df2ca12893d",
            "Unit does not exist",
            404,
        ),
        (
            "anonymous",
            "2ca850fa-ce19-4d8a-9dfd-8d54a261778d",
            "You do not have permission",
            403,
        ),
        (
            "anonymous",
            "fe3799b7-f061-42f2-b012-b569303f8a41",
            "You do not have permission",
            403,
        ),
        (
            "anonymous",
            "98a74429-2be2-44c0-8f7f-2df2ca12893d",
            "Unit does not exist",
            404,
        ),
        (
            "anonymous",
            "00000000-0000-0000-0000-000000000000",
            "Unit does not exist",
            404,
        ),
        (
            None,
            "2ca850fa-ce19-4d8a-9dfd-8d54a261778d",
            "You do not have permission",
            403,
        ),
        (
            None,
            "fe3799b7-f061-42f2-b012-b569303f8a41",
            "You do not have permission",
            403,
        ),
        (
            None,
            "98a74429-2be2-44c0-8f7f-2df2ca12893d",
            "Unit does not exist",
            404,
        ),
        (
            None,
            "00000000-0000-0000-0000-000000000000",
            "Unit does not exist",
            404,
        ),
    ],
)
def test_edit_unit(get_principal, principal, unit, message, error_code):
    unit_data = UnitPatchBody(
        name="New", symbol="New", definition="New", unit_type="New"
    )
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            unit_service.update(
                principal=get_principal(principal), uid=uuid.UUID(unit), data=unit_data
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        unit_update = unit_service.update(
            principal=get_principal(principal), uid=uuid.UUID(unit), data=unit_data
        )
        assert unit_update.definition == unit_data.definition
        assert unit_update.name == unit_data.name
        assert unit_update.symbol == unit_data.symbol
        assert unit_update.unit_type == unit_data.unit_type
        assert UnitGetResponse.from_orm(unit_update)


@pytest.mark.parametrize(
    "principal, unit, message, error_code",
    [
        (
            "owner",
            "2ca850fa-ce19-4d8a-9dfd-8d54a261778d",
            "You do not have permission",
            403,
        ),
        ("owner", "fe3799b7-f061-42f2-b012-b569303f8a41", None, None),
        ("owner", "98a74429-2be2-44c0-8f7f-2df2ca12893d", None, None),
        ("admin", "2ca850fa-ce19-4d8a-9dfd-8d54a261778d", None, None),
        ("admin", "fe3799b7-f061-42f2-b012-b569303f8a41", None, None),
        ("admin", "98a74429-2be2-44c0-8f7f-2df2ca12893d", None, None),
        (
            "admin",
            "85c4118e-d1cc-4003-bbc5-5c65af802ae0",
            "Unit in use by one or more datastreams",
            409,
        ),
        (
            "editor",
            "2ca850fa-ce19-4d8a-9dfd-8d54a261778d",
            "You do not have permission",
            403,
        ),
        ("editor", "fe3799b7-f061-42f2-b012-b569303f8a41", None, None),
        ("editor", "98a74429-2be2-44c0-8f7f-2df2ca12893d", None, None),
        (
            "viewer",
            "2ca850fa-ce19-4d8a-9dfd-8d54a261778d",
            "You do not have permission",
            403,
        ),
        (
            "viewer",
            "fe3799b7-f061-42f2-b012-b569303f8a41",
            "You do not have permission",
            403,
        ),
        (
            "viewer",
            "98a74429-2be2-44c0-8f7f-2df2ca12893d",
            "You do not have permission",
            403,
        ),
        (
            "apikey",
            "2ca850fa-ce19-4d8a-9dfd-8d54a261778d",
            "You do not have permission",
            403,
        ),
        (
            "apikey",
            "fe3799b7-f061-42f2-b012-b569303f8a41",
            "You do not have permission",
            403,
        ),
        (
            "apikey",
            "98a74429-2be2-44c0-8f7f-2df2ca12893d",
            "Unit does not exist",
            404,
        ),
        (
            "anonymous",
            "2ca850fa-ce19-4d8a-9dfd-8d54a261778d",
            "You do not have permission",
            403,
        ),
        (
            "anonymous",
            "fe3799b7-f061-42f2-b012-b569303f8a41",
            "You do not have permission",
            403,
        ),
        (
            "anonymous",
            "98a74429-2be2-44c0-8f7f-2df2ca12893d",
            "Unit does not exist",
            404,
        ),
        (
            "anonymous",
            "00000000-0000-0000-0000-000000000000",
            "Unit does not exist",
            404,
        ),
        (
            None,
            "2ca850fa-ce19-4d8a-9dfd-8d54a261778d",
            "You do not have permission",
            403,
        ),
        (
            None,
            "fe3799b7-f061-42f2-b012-b569303f8a41",
            "You do not have permission",
            403,
        ),
        (
            None,
            "98a74429-2be2-44c0-8f7f-2df2ca12893d",
            "Unit does not exist",
            404,
        ),
        (
            None,
            "00000000-0000-0000-0000-000000000000",
            "Unit does not exist",
            404,
        ),
    ],
)
def test_delete_unit(get_principal, principal, unit, message, error_code):
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            unit_service.delete(principal=get_principal(principal), uid=uuid.UUID(unit))
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        unit_delete = unit_service.delete(
            principal=get_principal(principal), uid=uuid.UUID(unit)
        )
        assert unit_delete == "Unit deleted"
