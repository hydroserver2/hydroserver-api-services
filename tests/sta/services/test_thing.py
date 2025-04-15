import pytest
import uuid
from ninja.errors import HttpError
from sta.services import ThingService
from sta.schemas import (
    ThingPostBody,
    ThingPatchBody,
    TagPostBody,
    TagDeleteBody,
    ThingGetResponse,
)

thing_service = ThingService()


@pytest.mark.parametrize(
    "user, workspace, length, max_queries",
    [
        ("owner", None, 4, 5),
        ("owner", "b27c51a0-7374-462d-8a53-d97d47176c10", 2, 5),
        ("owner", "caf4b92e-6914-4449-8c8a-efa5a7fd1826", 0, 2),
        ("admin", None, 4, 5),
        ("admin", "b27c51a0-7374-462d-8a53-d97d47176c10", 2, 5),
        ("admin", "caf4b92e-6914-4449-8c8a-efa5a7fd1826", 0, 2),
        ("editor", None, 4, 5),
        ("editor", "b27c51a0-7374-462d-8a53-d97d47176c10", 2, 5),
        ("viewer", None, 4, 5),
        ("viewer", "b27c51a0-7374-462d-8a53-d97d47176c10", 2, 5),
        ("anonymous", None, 1, 5),
        ("anonymous", "6e0deaf2-a92b-421b-9ece-86783265596f", 1, 5),
        ("anonymous", "b27c51a0-7374-462d-8a53-d97d47176c10", 0, 2),
        ("anonymous", "00000000-0000-0000-0000-000000000000", 0, 2),
        (None, None, 1, 5),
        (None, "6e0deaf2-a92b-421b-9ece-86783265596f", 1, 5),
        (None, "b27c51a0-7374-462d-8a53-d97d47176c10", 0, 2),
        (None, "00000000-0000-0000-0000-000000000000", 0, 2),
    ],
)
def test_list_thing(
    django_assert_max_num_queries, get_user, user, workspace, length, max_queries
):
    with django_assert_max_num_queries(max_queries):
        thing_list = thing_service.list(
            user=get_user(user),
            workspace_id=uuid.UUID(workspace) if workspace else None,
        )
        assert len(thing_list) == length
        assert (ThingGetResponse.from_orm(thing) for thing in thing_list)


@pytest.mark.parametrize(
    "user, thing, message, error_code",
    [
        (
            "owner",
            "3b7818af-eff7-4149-8517-e5cad9dc22e1",
            "Utah Water Research Lab",
            None,
        ),
        (
            "owner",
            "76dadda5-224b-4e1f-8570-e385bd482b2d",
            "Taggart Student Center",
            None,
        ),
        ("owner", "92a3a099-f2d3-40ec-9b0e-d25ae8bf59b7", "Old Main Building", None),
        (
            "owner",
            "819260c8-2543-4046-b8c4-7431243ed7c5",
            "Merrill-Cazier Library",
            None,
        ),
        (
            "admin",
            "3b7818af-eff7-4149-8517-e5cad9dc22e1",
            "Utah Water Research Lab",
            None,
        ),
        (
            "admin",
            "76dadda5-224b-4e1f-8570-e385bd482b2d",
            "Taggart Student Center",
            None,
        ),
        ("admin", "92a3a099-f2d3-40ec-9b0e-d25ae8bf59b7", "Old Main Building", None),
        (
            "admin",
            "819260c8-2543-4046-b8c4-7431243ed7c5",
            "Merrill-Cazier Library",
            None,
        ),
        (
            "editor",
            "3b7818af-eff7-4149-8517-e5cad9dc22e1",
            "Utah Water Research Lab",
            None,
        ),
        (
            "editor",
            "76dadda5-224b-4e1f-8570-e385bd482b2d",
            "Taggart Student Center",
            None,
        ),
        ("editor", "92a3a099-f2d3-40ec-9b0e-d25ae8bf59b7", "Old Main Building", None),
        (
            "editor",
            "819260c8-2543-4046-b8c4-7431243ed7c5",
            "Merrill-Cazier Library",
            None,
        ),
        (
            "viewer",
            "3b7818af-eff7-4149-8517-e5cad9dc22e1",
            "Utah Water Research Lab",
            None,
        ),
        (
            "viewer",
            "76dadda5-224b-4e1f-8570-e385bd482b2d",
            "Taggart Student Center",
            None,
        ),
        ("viewer", "92a3a099-f2d3-40ec-9b0e-d25ae8bf59b7", "Old Main Building", None),
        (
            "viewer",
            "819260c8-2543-4046-b8c4-7431243ed7c5",
            "Merrill-Cazier Library",
            None,
        ),
        (
            "anonymous",
            "3b7818af-eff7-4149-8517-e5cad9dc22e1",
            "Utah Water Research Lab",
            None,
        ),
        (
            "anonymous",
            "76dadda5-224b-4e1f-8570-e385bd482b2d",
            "Thing does not exist",
            404,
        ),
        (
            "anonymous",
            "92a3a099-f2d3-40ec-9b0e-d25ae8bf59b7",
            "Thing does not exist",
            404,
        ),
        (
            "anonymous",
            "819260c8-2543-4046-b8c4-7431243ed7c5",
            "Thing does not exist",
            404,
        ),
        (
            "anonymous",
            "00000000-0000-0000-0000-000000000000",
            "Thing does not exist",
            404,
        ),
        (
            None,
            "3b7818af-eff7-4149-8517-e5cad9dc22e1",
            "Utah Water Research Lab",
            None,
        ),
        (
            None,
            "76dadda5-224b-4e1f-8570-e385bd482b2d",
            "Thing does not exist",
            404,
        ),
        (
            None,
            "92a3a099-f2d3-40ec-9b0e-d25ae8bf59b7",
            "Thing does not exist",
            404,
        ),
        (
            None,
            "819260c8-2543-4046-b8c4-7431243ed7c5",
            "Thing does not exist",
            404,
        ),
        (
            None,
            "00000000-0000-0000-0000-000000000000",
            "Thing does not exist",
            404,
        ),
    ],
)
def test_get_thing(get_user, user, thing, message, error_code):
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            thing_service.get(user=get_user(user), uid=uuid.UUID(thing))
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        thing_get = thing_service.get(user=get_user(user), uid=uuid.UUID(thing))
        assert thing_get.name == message
        assert ThingGetResponse.from_orm(thing_get)


@pytest.mark.parametrize(
    "user, workspace, message, error_code",
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
def test_create_thing(get_user, user, workspace, message, error_code):
    thing_data = ThingPostBody(
        name="New",
        description="New",
        sampling_feature_type="Site",
        sampling_feature_code="NEW",
        site_type="Site",
        latitude=0,
        longitude=0,
        is_private=False,
        workspace_id=uuid.UUID(workspace),
    )
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            thing_service.create(user=get_user(user), data=thing_data)
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        thing_create = thing_service.create(user=get_user(user), data=thing_data)
        assert thing_create.name == thing_data.name
        assert thing_create.description == thing_data.description
        assert thing_create.sampling_feature_type == thing_data.sampling_feature_type
        assert thing_create.sampling_feature_code == thing_data.sampling_feature_code
        assert thing_create.site_type == thing_data.site_type
        assert thing_create.location.latitude == thing_data.latitude
        assert thing_create.location.longitude == thing_data.longitude
        assert thing_create.is_private == thing_data.is_private
        assert thing_create.workspace_id == thing_data.workspace_id
        assert ThingGetResponse.from_orm(thing_create)


@pytest.mark.parametrize(
    "user, thing, message, error_code",
    [
        ("owner", "3b7818af-eff7-4149-8517-e5cad9dc22e1", None, None),
        ("owner", "76dadda5-224b-4e1f-8570-e385bd482b2d", None, None),
        ("owner", "92a3a099-f2d3-40ec-9b0e-d25ae8bf59b7", None, None),
        ("owner", "819260c8-2543-4046-b8c4-7431243ed7c5", None, None),
        ("admin", "3b7818af-eff7-4149-8517-e5cad9dc22e1", None, None),
        ("admin", "76dadda5-224b-4e1f-8570-e385bd482b2d", None, None),
        ("admin", "92a3a099-f2d3-40ec-9b0e-d25ae8bf59b7", None, None),
        ("admin", "819260c8-2543-4046-b8c4-7431243ed7c5", None, None),
        ("editor", "3b7818af-eff7-4149-8517-e5cad9dc22e1", None, None),
        ("editor", "76dadda5-224b-4e1f-8570-e385bd482b2d", None, None),
        ("editor", "92a3a099-f2d3-40ec-9b0e-d25ae8bf59b7", None, None),
        ("editor", "819260c8-2543-4046-b8c4-7431243ed7c5", None, None),
        (
            "viewer",
            "3b7818af-eff7-4149-8517-e5cad9dc22e1",
            "You do not have permission",
            403,
        ),
        (
            "viewer",
            "76dadda5-224b-4e1f-8570-e385bd482b2d",
            "You do not have permission",
            403,
        ),
        (
            "viewer",
            "92a3a099-f2d3-40ec-9b0e-d25ae8bf59b7",
            "You do not have permission",
            403,
        ),
        (
            "viewer",
            "819260c8-2543-4046-b8c4-7431243ed7c5",
            "You do not have permission",
            403,
        ),
        (
            "anonymous",
            "3b7818af-eff7-4149-8517-e5cad9dc22e1",
            "You do not have permission",
            403,
        ),
        (
            "anonymous",
            "76dadda5-224b-4e1f-8570-e385bd482b2d",
            "Thing does not exist",
            404,
        ),
        (
            "anonymous",
            "92a3a099-f2d3-40ec-9b0e-d25ae8bf59b7",
            "Thing does not exist",
            404,
        ),
        (
            "anonymous",
            "819260c8-2543-4046-b8c4-7431243ed7c5",
            "Thing does not exist",
            404,
        ),
        (
            "anonymous",
            "00000000-0000-0000-0000-000000000000",
            "Thing does not exist",
            404,
        ),
        (
            None,
            "3b7818af-eff7-4149-8517-e5cad9dc22e1",
            "You do not have permission",
            403,
        ),
        (
            None,
            "76dadda5-224b-4e1f-8570-e385bd482b2d",
            "Thing does not exist",
            404,
        ),
        (
            None,
            "92a3a099-f2d3-40ec-9b0e-d25ae8bf59b7",
            "Thing does not exist",
            404,
        ),
        (
            None,
            "819260c8-2543-4046-b8c4-7431243ed7c5",
            "Thing does not exist",
            404,
        ),
        (
            None,
            "00000000-0000-0000-0000-000000000000",
            "Thing does not exist",
            404,
        ),
    ],
)
def test_edit_thing(get_user, user, thing, message, error_code):
    thing_data = ThingPatchBody(
        name="New",
        description="New",
        sampling_feature_type="Site",
        sampling_feature_code="NEW",
        site_type="Site",
        latitude=0,
        longitude=0,
        is_private=False,
    )
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            thing_service.update(
                user=get_user(user), uid=uuid.UUID(thing), data=thing_data
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        thing_update = thing_service.update(
            user=get_user(user), uid=uuid.UUID(thing), data=thing_data
        )
        assert thing_update.name == thing_data.name
        assert thing_update.description == thing_data.description
        assert thing_update.sampling_feature_type == thing_data.sampling_feature_type
        assert thing_update.sampling_feature_code == thing_data.sampling_feature_code
        assert thing_update.site_type == thing_data.site_type
        assert thing_update.location.latitude == thing_data.latitude
        assert thing_update.location.longitude == thing_data.longitude
        assert thing_update.is_private == thing_data.is_private
        assert ThingGetResponse.from_orm(thing_update)


@pytest.mark.parametrize(
    "user, thing, message, error_code, max_queries",
    [
        ("owner", "3b7818af-eff7-4149-8517-e5cad9dc22e1", None, None, 16),
        ("owner", "76dadda5-224b-4e1f-8570-e385bd482b2d", None, None, 16),
        ("owner", "92a3a099-f2d3-40ec-9b0e-d25ae8bf59b7", None, None, 16),
        ("owner", "819260c8-2543-4046-b8c4-7431243ed7c5", None, None, 16),
        ("admin", "3b7818af-eff7-4149-8517-e5cad9dc22e1", None, None, 16),
        ("admin", "76dadda5-224b-4e1f-8570-e385bd482b2d", None, None, 16),
        ("admin", "92a3a099-f2d3-40ec-9b0e-d25ae8bf59b7", None, None, 16),
        ("admin", "819260c8-2543-4046-b8c4-7431243ed7c5", None, None, 16),
        ("editor", "3b7818af-eff7-4149-8517-e5cad9dc22e1", None, None, 17),
        ("editor", "76dadda5-224b-4e1f-8570-e385bd482b2d", None, None, 17),
        ("editor", "92a3a099-f2d3-40ec-9b0e-d25ae8bf59b7", None, None, 17),
        ("editor", "819260c8-2543-4046-b8c4-7431243ed7c5", None, None, 17),
        (
            "viewer",
            "3b7818af-eff7-4149-8517-e5cad9dc22e1",
            "You do not have permission",
            403,
            6,
        ),
        (
            "viewer",
            "76dadda5-224b-4e1f-8570-e385bd482b2d",
            "You do not have permission",
            403,
            6,
        ),
        (
            "viewer",
            "92a3a099-f2d3-40ec-9b0e-d25ae8bf59b7",
            "You do not have permission",
            403,
            6,
        ),
        (
            "viewer",
            "819260c8-2543-4046-b8c4-7431243ed7c5",
            "You do not have permission",
            403,
            6,
        ),
        (
            "anonymous",
            "3b7818af-eff7-4149-8517-e5cad9dc22e1",
            "You do not have permission",
            403,
            6,
        ),
        (
            "anonymous",
            "76dadda5-224b-4e1f-8570-e385bd482b2d",
            "Thing does not exist",
            404,
            6,
        ),
        (
            "anonymous",
            "92a3a099-f2d3-40ec-9b0e-d25ae8bf59b7",
            "Thing does not exist",
            404,
            6,
        ),
        (
            "anonymous",
            "819260c8-2543-4046-b8c4-7431243ed7c5",
            "Thing does not exist",
            404,
            6,
        ),
        (
            "anonymous",
            "00000000-0000-0000-0000-000000000000",
            "Thing does not exist",
            404,
            6,
        ),
        (
            None,
            "3b7818af-eff7-4149-8517-e5cad9dc22e1",
            "You do not have permission",
            403,
            6,
        ),
        (
            None,
            "76dadda5-224b-4e1f-8570-e385bd482b2d",
            "Thing does not exist",
            404,
            6,
        ),
        (
            None,
            "92a3a099-f2d3-40ec-9b0e-d25ae8bf59b7",
            "Thing does not exist",
            404,
            6,
        ),
        (
            None,
            "819260c8-2543-4046-b8c4-7431243ed7c5",
            "Thing does not exist",
            404,
            6,
        ),
        (
            None,
            "00000000-0000-0000-0000-000000000000",
            "Thing does not exist",
            404,
            6,
        ),
    ],
)
def test_delete_thing(
    django_assert_max_num_queries,
    get_user,
    user,
    thing,
    message,
    error_code,
    max_queries,
):
    with django_assert_max_num_queries(max_queries):
        if error_code:
            with pytest.raises(HttpError) as exc_info:
                thing_service.delete(user=get_user(user), uid=uuid.UUID(thing))
            assert exc_info.value.status_code == error_code
            assert exc_info.value.message.startswith(message)
        else:
            thing_delete = thing_service.delete(
                user=get_user(user), uid=uuid.UUID(thing)
            )
            assert thing_delete == "Thing deleted"


@pytest.mark.parametrize(
    "user, thing, message, error_code",
    [
        ("owner", "3b7818af-eff7-4149-8517-e5cad9dc22e1", None, None),
        ("owner", "76dadda5-224b-4e1f-8570-e385bd482b2d", None, None),
        ("owner", "92a3a099-f2d3-40ec-9b0e-d25ae8bf59b7", None, None),
        ("owner", "819260c8-2543-4046-b8c4-7431243ed7c5", None, None),
        ("admin", "3b7818af-eff7-4149-8517-e5cad9dc22e1", None, None),
        ("admin", "76dadda5-224b-4e1f-8570-e385bd482b2d", None, None),
        ("admin", "92a3a099-f2d3-40ec-9b0e-d25ae8bf59b7", None, None),
        ("admin", "819260c8-2543-4046-b8c4-7431243ed7c5", None, None),
        ("editor", "3b7818af-eff7-4149-8517-e5cad9dc22e1", None, None),
        ("editor", "76dadda5-224b-4e1f-8570-e385bd482b2d", None, None),
        ("editor", "92a3a099-f2d3-40ec-9b0e-d25ae8bf59b7", None, None),
        ("editor", "819260c8-2543-4046-b8c4-7431243ed7c5", None, None),
        ("viewer", "3b7818af-eff7-4149-8517-e5cad9dc22e1", None, None),
        ("viewer", "76dadda5-224b-4e1f-8570-e385bd482b2d", None, None),
        ("viewer", "92a3a099-f2d3-40ec-9b0e-d25ae8bf59b7", None, None),
        ("viewer", "819260c8-2543-4046-b8c4-7431243ed7c5", None, None),
        ("anonymous", "3b7818af-eff7-4149-8517-e5cad9dc22e1", None, None),
        (
            "anonymous",
            "76dadda5-224b-4e1f-8570-e385bd482b2d",
            "Thing does not exist",
            404,
        ),
        (
            "anonymous",
            "92a3a099-f2d3-40ec-9b0e-d25ae8bf59b7",
            "Thing does not exist",
            404,
        ),
        (
            "anonymous",
            "819260c8-2543-4046-b8c4-7431243ed7c5",
            "Thing does not exist",
            404,
        ),
        (None, "3b7818af-eff7-4149-8517-e5cad9dc22e1", None, None),
        (
            None,
            "76dadda5-224b-4e1f-8570-e385bd482b2d",
            "Thing does not exist",
            404,
        ),
        (
            None,
            "92a3a099-f2d3-40ec-9b0e-d25ae8bf59b7",
            "Thing does not exist",
            404,
        ),
        (
            None,
            "819260c8-2543-4046-b8c4-7431243ed7c5",
            "Thing does not exist",
            404,
        ),
    ],
)
def test_get_tags(get_user, user, thing, message, error_code):
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            thing_service.get_tags(user=get_user(user), uid=uuid.UUID(thing))
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        thing_tags = thing_service.get_tags(user=get_user(user), uid=uuid.UUID(thing))
        assert len(list(thing_tags.all())) == 1
        assert list(thing_tags.all())[0].key in ["Test Public Key", "Test Private Key"]
        assert list(thing_tags.all())[0].value in [
            "Test Public Value",
            "Test Private Value",
        ]


@pytest.mark.parametrize(
    "user, workspace, thing, length, max_queries",
    [
        ("owner", None, None, 2, 2),
        ("owner", "b27c51a0-7374-462d-8a53-d97d47176c10", None, 1, 2),
        ("owner", None, "76dadda5-224b-4e1f-8570-e385bd482b2d", 1, 2),
        (
            "owner",
            "6e0deaf2-a92b-421b-9ece-86783265596f",
            "76dadda5-224b-4e1f-8570-e385bd482b2d",
            0,
            2,
        ),
        ("admin", None, None, 2, 2),
        ("admin", "b27c51a0-7374-462d-8a53-d97d47176c10", None, 1, 2),
        ("admin", None, "76dadda5-224b-4e1f-8570-e385bd482b2d", 1, 2),
        (
            "admin",
            "6e0deaf2-a92b-421b-9ece-86783265596f",
            "76dadda5-224b-4e1f-8570-e385bd482b2d",
            0,
            2,
        ),
        ("editor", None, None, 2, 2),
        ("editor", "b27c51a0-7374-462d-8a53-d97d47176c10", None, 1, 2),
        ("editor", None, "76dadda5-224b-4e1f-8570-e385bd482b2d", 1, 2),
        (
            "editor",
            "6e0deaf2-a92b-421b-9ece-86783265596f",
            "76dadda5-224b-4e1f-8570-e385bd482b2d",
            0,
            2,
        ),
        ("viewer", None, None, 2, 2),
        ("viewer", "b27c51a0-7374-462d-8a53-d97d47176c10", None, 1, 2),
        ("viewer", None, "76dadda5-224b-4e1f-8570-e385bd482b2d", 1, 2),
        (
            "viewer",
            "6e0deaf2-a92b-421b-9ece-86783265596f",
            "76dadda5-224b-4e1f-8570-e385bd482b2d",
            0,
            2,
        ),
        ("anonymous", None, None, 1, 2),
        ("anonymous", "b27c51a0-7374-462d-8a53-d97d47176c10", None, 0, 2),
        ("anonymous", None, "76dadda5-224b-4e1f-8570-e385bd482b2d", 0, 2),
        (
            "anonymous",
            "6e0deaf2-a92b-421b-9ece-86783265596f",
            "76dadda5-224b-4e1f-8570-e385bd482b2d",
            0,
            2,
        ),
        (None, None, None, 1, 2),
        (None, "b27c51a0-7374-462d-8a53-d97d47176c10", None, 0, 2),
        (None, None, "76dadda5-224b-4e1f-8570-e385bd482b2d", 0, 2),
        (
            None,
            "6e0deaf2-a92b-421b-9ece-86783265596f",
            "76dadda5-224b-4e1f-8570-e385bd482b2d",
            0,
            2,
        ),
    ],
)
def test_get_tag_keys(
    django_assert_num_queries, get_user, user, workspace, thing, length, max_queries
):
    with django_assert_num_queries(max_queries):
        tag_key_list = thing_service.get_tag_keys(
            user=get_user(user),
            workspace_id=uuid.UUID(workspace) if workspace else None,
            thing_id=uuid.UUID(thing) if thing else None,
        )
        assert len(tag_key_list) == length
        assert (isinstance(str, tag_key) for tag_key in tag_key_list)


@pytest.mark.parametrize(
    "user, thing, tag, message, error_code",
    [
        (
            "owner",
            "3b7818af-eff7-4149-8517-e5cad9dc22e1",
            {"key": "New Key", "value": "New Value"},
            None,
            None,
        ),
        (
            "owner",
            "3b7818af-eff7-4149-8517-e5cad9dc22e1",
            {"key": "New Key", "value": "Test Value"},
            None,
            None,
        ),
        (
            "owner",
            "3b7818af-eff7-4149-8517-e5cad9dc22e1",
            {"key": "Test Public Key", "value": "New Value"},
            "Tag already exists",
            400,
        ),
        (
            "owner",
            "76dadda5-224b-4e1f-8570-e385bd482b2d",
            {"key": "New Key", "value": "New Value"},
            None,
            None,
        ),
        (
            "owner",
            "92a3a099-f2d3-40ec-9b0e-d25ae8bf59b7",
            {"key": "New Key", "value": "New Value"},
            None,
            None,
        ),
        (
            "owner",
            "819260c8-2543-4046-b8c4-7431243ed7c5",
            {"key": "New Key", "value": "New Value"},
            None,
            None,
        ),
        (
            "admin",
            "3b7818af-eff7-4149-8517-e5cad9dc22e1",
            {"key": "New Key", "value": "New Value"},
            None,
            None,
        ),
        (
            "admin",
            "76dadda5-224b-4e1f-8570-e385bd482b2d",
            {"key": "New Key", "value": "New Value"},
            None,
            None,
        ),
        (
            "admin",
            "92a3a099-f2d3-40ec-9b0e-d25ae8bf59b7",
            {"key": "New Key", "value": "New Value"},
            None,
            None,
        ),
        (
            "admin",
            "819260c8-2543-4046-b8c4-7431243ed7c5",
            {"key": "New Key", "value": "New Value"},
            None,
            None,
        ),
        (
            "editor",
            "3b7818af-eff7-4149-8517-e5cad9dc22e1",
            {"key": "New Key", "value": "New Value"},
            None,
            None,
        ),
        (
            "editor",
            "76dadda5-224b-4e1f-8570-e385bd482b2d",
            {"key": "New Key", "value": "New Value"},
            None,
            None,
        ),
        (
            "editor",
            "92a3a099-f2d3-40ec-9b0e-d25ae8bf59b7",
            {"key": "New Key", "value": "New Value"},
            None,
            None,
        ),
        (
            "editor",
            "819260c8-2543-4046-b8c4-7431243ed7c5",
            {"key": "New Key", "value": "New Value"},
            None,
            None,
        ),
        (
            "viewer",
            "3b7818af-eff7-4149-8517-e5cad9dc22e1",
            {"key": "New Key", "value": "New Value"},
            "You do not have permission",
            403,
        ),
        (
            "viewer",
            "76dadda5-224b-4e1f-8570-e385bd482b2d",
            {"key": "New Key", "value": "New Value"},
            "You do not have permission",
            403,
        ),
        (
            "viewer",
            "92a3a099-f2d3-40ec-9b0e-d25ae8bf59b7",
            {"key": "New Key", "value": "New Value"},
            "You do not have permission",
            403,
        ),
        (
            "viewer",
            "819260c8-2543-4046-b8c4-7431243ed7c5",
            {"key": "New Key", "value": "New Value"},
            "You do not have permission",
            403,
        ),
        (
            "anonymous",
            "3b7818af-eff7-4149-8517-e5cad9dc22e1",
            {"key": "New Key", "value": "New Value"},
            "You do not have permission",
            403,
        ),
        (
            "anonymous",
            "76dadda5-224b-4e1f-8570-e385bd482b2d",
            {"key": "New Key", "value": "New Value"},
            "Thing does not exist",
            404,
        ),
        (
            "anonymous",
            "92a3a099-f2d3-40ec-9b0e-d25ae8bf59b7",
            {"key": "New Key", "value": "New Value"},
            "Thing does not exist",
            404,
        ),
        (
            "anonymous",
            "819260c8-2543-4046-b8c4-7431243ed7c5",
            {"key": "New Key", "value": "New Value"},
            "Thing does not exist",
            404,
        ),
        (
            None,
            "3b7818af-eff7-4149-8517-e5cad9dc22e1",
            {"key": "New Key", "value": "New Value"},
            "You do not have permission",
            403,
        ),
        (
            None,
            "76dadda5-224b-4e1f-8570-e385bd482b2d",
            {"key": "New Key", "value": "New Value"},
            "Thing does not exist",
            404,
        ),
        (
            None,
            "92a3a099-f2d3-40ec-9b0e-d25ae8bf59b7",
            {"key": "New Key", "value": "New Value"},
            "Thing does not exist",
            404,
        ),
        (
            None,
            "819260c8-2543-4046-b8c4-7431243ed7c5",
            {"key": "New Key", "value": "New Value"},
            "Thing does not exist",
            404,
        ),
    ],
)
def test_add_tag(get_user, user, thing, tag, message, error_code):
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            thing_service.add_tag(
                user=get_user(user),
                uid=uuid.UUID(thing),
                data=TagPostBody(key=tag["key"], value=tag["value"]),
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        thing_tag = thing_service.add_tag(
            user=get_user(user),
            uid=uuid.UUID(thing),
            data=TagPostBody(key=tag["key"], value=tag["value"]),
        )

        assert thing_tag.key == tag["key"]
        assert thing_tag.value == tag["value"]


@pytest.mark.parametrize(
    "user, thing, tag, message, error_code",
    [
        (
            "owner",
            "3b7818af-eff7-4149-8517-e5cad9dc22e1",
            {"key": "Test Public Key", "value": "New Value"},
            None,
            None,
        ),
        (
            "owner",
            "3b7818af-eff7-4149-8517-e5cad9dc22e1",
            {"key": "Test Public Key", "value": "New Value"},
            None,
            None,
        ),
        (
            "owner",
            "3b7818af-eff7-4149-8517-e5cad9dc22e1",
            {"key": "New Key", "value": "New Value"},
            "Tag does not exist",
            404,
        ),
        (
            "owner",
            "76dadda5-224b-4e1f-8570-e385bd482b2d",
            {"key": "Test Private Key", "value": "New Value"},
            None,
            None,
        ),
        (
            "owner",
            "92a3a099-f2d3-40ec-9b0e-d25ae8bf59b7",
            {"key": "Test Private Key", "value": "New Value"},
            None,
            None,
        ),
        (
            "owner",
            "819260c8-2543-4046-b8c4-7431243ed7c5",
            {"key": "Test Private Key", "value": "New Value"},
            None,
            None,
        ),
        (
            "admin",
            "3b7818af-eff7-4149-8517-e5cad9dc22e1",
            {"key": "Test Public Key", "value": "New Value"},
            None,
            None,
        ),
        (
            "admin",
            "76dadda5-224b-4e1f-8570-e385bd482b2d",
            {"key": "Test Private Key", "value": "New Value"},
            None,
            None,
        ),
        (
            "admin",
            "92a3a099-f2d3-40ec-9b0e-d25ae8bf59b7",
            {"key": "Test Private Key", "value": "New Value"},
            None,
            None,
        ),
        (
            "admin",
            "819260c8-2543-4046-b8c4-7431243ed7c5",
            {"key": "Test Private Key", "value": "New Value"},
            None,
            None,
        ),
        (
            "editor",
            "3b7818af-eff7-4149-8517-e5cad9dc22e1",
            {"key": "Test Public Key", "value": "New Value"},
            None,
            None,
        ),
        (
            "editor",
            "76dadda5-224b-4e1f-8570-e385bd482b2d",
            {"key": "Test Private Key", "value": "New Value"},
            None,
            None,
        ),
        (
            "editor",
            "92a3a099-f2d3-40ec-9b0e-d25ae8bf59b7",
            {"key": "Test Private Key", "value": "New Value"},
            None,
            None,
        ),
        (
            "editor",
            "819260c8-2543-4046-b8c4-7431243ed7c5",
            {"key": "Test Private Key", "value": "New Value"},
            None,
            None,
        ),
        (
            "viewer",
            "3b7818af-eff7-4149-8517-e5cad9dc22e1",
            {"key": "Test Public Key", "value": "New Value"},
            "You do not have permission",
            403,
        ),
        (
            "viewer",
            "76dadda5-224b-4e1f-8570-e385bd482b2d",
            {"key": "Test Private Key", "value": "New Value"},
            "You do not have permission",
            403,
        ),
        (
            "viewer",
            "92a3a099-f2d3-40ec-9b0e-d25ae8bf59b7",
            {"key": "Test Private Key", "value": "New Value"},
            "You do not have permission",
            403,
        ),
        (
            "viewer",
            "819260c8-2543-4046-b8c4-7431243ed7c5",
            {"key": "Test Private Key", "value": "New Value"},
            "You do not have permission",
            403,
        ),
        (
            "anonymous",
            "3b7818af-eff7-4149-8517-e5cad9dc22e1",
            {"key": "Test Public Key", "value": "New Value"},
            "You do not have permission",
            403,
        ),
        (
            "anonymous",
            "76dadda5-224b-4e1f-8570-e385bd482b2d",
            {"key": "Test Private Key", "value": "New Value"},
            "Thing does not exist",
            404,
        ),
        (
            "anonymous",
            "92a3a099-f2d3-40ec-9b0e-d25ae8bf59b7",
            {"key": "Test Private Key", "value": "New Value"},
            "Thing does not exist",
            404,
        ),
        (
            "anonymous",
            "819260c8-2543-4046-b8c4-7431243ed7c5",
            {"key": "Test Private Key", "value": "New Value"},
            "Thing does not exist",
            404,
        ),
        (
            None,
            "3b7818af-eff7-4149-8517-e5cad9dc22e1",
            {"key": "Test Public Key", "value": "New Value"},
            "You do not have permission",
            403,
        ),
        (
            None,
            "76dadda5-224b-4e1f-8570-e385bd482b2d",
            {"key": "Test Private Key", "value": "New Value"},
            "Thing does not exist",
            404,
        ),
        (
            None,
            "92a3a099-f2d3-40ec-9b0e-d25ae8bf59b7",
            {"key": "Test Private Key", "value": "New Value"},
            "Thing does not exist",
            404,
        ),
        (
            None,
            "819260c8-2543-4046-b8c4-7431243ed7c5",
            {"key": "Test Private Key", "value": "New Value"},
            "Thing does not exist",
            404,
        ),
    ],
)
def test_update_tag(get_user, user, thing, tag, message, error_code):
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            thing_service.update_tag(
                user=get_user(user),
                uid=uuid.UUID(thing),
                data=TagPostBody(key=tag["key"], value=tag["value"]),
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        thing_tag = thing_service.update_tag(
            user=get_user(user),
            uid=uuid.UUID(thing),
            data=TagPostBody(key=tag["key"], value=tag["value"]),
        )

        assert thing_tag.key == tag["key"]
        assert thing_tag.value == tag["value"]


@pytest.mark.parametrize(
    "user, thing, tag, message, error_code",
    [
        (
            "owner",
            "3b7818af-eff7-4149-8517-e5cad9dc22e1",
            {"key": "Test Public Key"},
            None,
            None,
        ),
        (
            "owner",
            "3b7818af-eff7-4149-8517-e5cad9dc22e1",
            {"key": "Test Public Key"},
            None,
            None,
        ),
        (
            "owner",
            "3b7818af-eff7-4149-8517-e5cad9dc22e1",
            {"key": "New Key"},
            "Tag does not exist",
            404,
        ),
        (
            "owner",
            "76dadda5-224b-4e1f-8570-e385bd482b2d",
            {"key": "Test Private Key"},
            None,
            None,
        ),
        (
            "owner",
            "92a3a099-f2d3-40ec-9b0e-d25ae8bf59b7",
            {"key": "Test Private Key"},
            None,
            None,
        ),
        (
            "owner",
            "819260c8-2543-4046-b8c4-7431243ed7c5",
            {"key": "Test Private Key"},
            None,
            None,
        ),
        (
            "admin",
            "3b7818af-eff7-4149-8517-e5cad9dc22e1",
            {"key": "Test Public Key"},
            None,
            None,
        ),
        (
            "admin",
            "76dadda5-224b-4e1f-8570-e385bd482b2d",
            {"key": "Test Private Key"},
            None,
            None,
        ),
        (
            "admin",
            "92a3a099-f2d3-40ec-9b0e-d25ae8bf59b7",
            {"key": "Test Private Key"},
            None,
            None,
        ),
        (
            "admin",
            "819260c8-2543-4046-b8c4-7431243ed7c5",
            {"key": "Test Private Key"},
            None,
            None,
        ),
        (
            "editor",
            "3b7818af-eff7-4149-8517-e5cad9dc22e1",
            {"key": "Test Public Key"},
            None,
            None,
        ),
        (
            "editor",
            "76dadda5-224b-4e1f-8570-e385bd482b2d",
            {"key": "Test Private Key"},
            None,
            None,
        ),
        (
            "editor",
            "92a3a099-f2d3-40ec-9b0e-d25ae8bf59b7",
            {"key": "Test Private Key"},
            None,
            None,
        ),
        (
            "editor",
            "819260c8-2543-4046-b8c4-7431243ed7c5",
            {"key": "Test Private Key"},
            None,
            None,
        ),
        (
            "viewer",
            "3b7818af-eff7-4149-8517-e5cad9dc22e1",
            {"key": "Test Public Key"},
            "You do not have permission",
            403,
        ),
        (
            "viewer",
            "76dadda5-224b-4e1f-8570-e385bd482b2d",
            {"key": "Test Private Key"},
            "You do not have permission",
            403,
        ),
        (
            "viewer",
            "92a3a099-f2d3-40ec-9b0e-d25ae8bf59b7",
            {"key": "Test Private Key"},
            "You do not have permission",
            403,
        ),
        (
            "viewer",
            "819260c8-2543-4046-b8c4-7431243ed7c5",
            {"key": "Test Private Key"},
            "You do not have permission",
            403,
        ),
        (
            "anonymous",
            "3b7818af-eff7-4149-8517-e5cad9dc22e1",
            {"key": "Test Public Key"},
            "You do not have permission",
            403,
        ),
        (
            "anonymous",
            "76dadda5-224b-4e1f-8570-e385bd482b2d",
            {"key": "Test Private Key"},
            "Thing does not exist",
            404,
        ),
        (
            "anonymous",
            "92a3a099-f2d3-40ec-9b0e-d25ae8bf59b7",
            {"key": "Test Private Key"},
            "Thing does not exist",
            404,
        ),
        (
            "anonymous",
            "819260c8-2543-4046-b8c4-7431243ed7c5",
            {"key": "Test Private Key"},
            "Thing does not exist",
            404,
        ),
        (
            None,
            "3b7818af-eff7-4149-8517-e5cad9dc22e1",
            {"key": "Test Public Key"},
            "You do not have permission",
            403,
        ),
        (
            None,
            "76dadda5-224b-4e1f-8570-e385bd482b2d",
            {"key": "Test Private Key"},
            "Thing does not exist",
            404,
        ),
        (
            None,
            "92a3a099-f2d3-40ec-9b0e-d25ae8bf59b7",
            {"key": "Test Private Key"},
            "Thing does not exist",
            404,
        ),
        (
            None,
            "819260c8-2543-4046-b8c4-7431243ed7c5",
            {"key": "Test Private Key"},
            "Thing does not exist",
            404,
        ),
    ],
)
def test_remove_tag(get_user, user, thing, tag, message, error_code):
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            thing_service.remove_tag(
                user=get_user(user),
                uid=uuid.UUID(thing),
                data=TagDeleteBody(key=tag["key"]),
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        thing_tag_delete = thing_service.remove_tag(
            user=get_user(user),
            uid=uuid.UUID(thing),
            data=TagDeleteBody(key=tag["key"]),
        )

        assert thing_tag_delete == "Tag deleted"
