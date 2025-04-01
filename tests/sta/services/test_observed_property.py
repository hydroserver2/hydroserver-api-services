import pytest
import uuid
from ninja.errors import HttpError
from sta.services import ObservedPropertyService
from sta.schemas import (
    ObservedPropertyPostBody,
    ObservedPropertyPatchBody,
    ObservedPropertyGetResponse,
)

observed_property_service = ObservedPropertyService()


@pytest.mark.parametrize(
    "user, workspace, length, max_queries",
    [
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
        (None, None, 4, 2),
        (None, "6e0deaf2-a92b-421b-9ece-86783265596f", 2, 2),
        (None, "b27c51a0-7374-462d-8a53-d97d47176c10", 0, 2),
        (None, "00000000-0000-0000-0000-000000000000", 0, 2),
    ],
)
def test_list_observed_property(
    django_assert_num_queries, get_user, user, workspace, length, max_queries
):
    with django_assert_num_queries(max_queries):
        observed_property_list = observed_property_service.list(
            user=get_user(user),
            workspace_id=uuid.UUID(workspace) if workspace else None,
        )
        assert len(observed_property_list) == length
        assert (
            ObservedPropertyGetResponse.from_orm(observed_property)
            for observed_property in observed_property_list
        )


@pytest.mark.parametrize(
    "user, observed_property, message, error_code",
    [
        (
            "owner",
            "49a245bd-4517-4dea-b3ba-25c919bf2cf5",
            "System Observed Property",
            None,
        ),
        (
            "owner",
            "cac1262e-68ee-43a0-9222-f214f2161091",
            "Public Observed Property",
            None,
        ),
        (
            "owner",
            "5dbfd184-ae79-4c05-a9ea-3f5e775ecbc1",
            "Private Observed Property",
            None,
        ),
        (
            "admin",
            "49a245bd-4517-4dea-b3ba-25c919bf2cf5",
            "System Observed Property",
            None,
        ),
        (
            "admin",
            "cac1262e-68ee-43a0-9222-f214f2161091",
            "Public Observed Property",
            None,
        ),
        (
            "admin",
            "5dbfd184-ae79-4c05-a9ea-3f5e775ecbc1",
            "Private Observed Property",
            None,
        ),
        (
            "editor",
            "49a245bd-4517-4dea-b3ba-25c919bf2cf5",
            "System Observed Property",
            None,
        ),
        (
            "editor",
            "cac1262e-68ee-43a0-9222-f214f2161091",
            "Public Observed Property",
            None,
        ),
        (
            "editor",
            "5dbfd184-ae79-4c05-a9ea-3f5e775ecbc1",
            "Private Observed Property",
            None,
        ),
        (
            "viewer",
            "49a245bd-4517-4dea-b3ba-25c919bf2cf5",
            "System Observed Property",
            None,
        ),
        (
            "viewer",
            "cac1262e-68ee-43a0-9222-f214f2161091",
            "Public Observed Property",
            None,
        ),
        (
            "viewer",
            "5dbfd184-ae79-4c05-a9ea-3f5e775ecbc1",
            "Private Observed Property",
            None,
        ),
        (
            "anonymous",
            "49a245bd-4517-4dea-b3ba-25c919bf2cf5",
            "System Observed Property",
            None,
        ),
        (
            "anonymous",
            "cac1262e-68ee-43a0-9222-f214f2161091",
            "Public Observed Property",
            None,
        ),
        (
            "anonymous",
            "5dbfd184-ae79-4c05-a9ea-3f5e775ecbc1",
            "Observed property does not exist",
            404,
        ),
        (
            "anonymous",
            "00000000-0000-0000-0000-000000000000",
            "Observed property does not exist",
            404,
        ),
        (
            None,
            "49a245bd-4517-4dea-b3ba-25c919bf2cf5",
            "System Observed Property",
            None,
        ),
        (
            None,
            "cac1262e-68ee-43a0-9222-f214f2161091",
            "Public Observed Property",
            None,
        ),
        (
            None,
            "5dbfd184-ae79-4c05-a9ea-3f5e775ecbc1",
            "Observed property does not exist",
            404,
        ),
        (
            None,
            "00000000-0000-0000-0000-000000000000",
            "Observed property does not exist",
            404,
        ),
    ],
)
def test_get_observed_property(get_user, user, observed_property, message, error_code):
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            observed_property_service.get(
                user=get_user(user), uid=uuid.UUID(observed_property)
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        observed_property_get = observed_property_service.get(
            user=get_user(user), uid=uuid.UUID(observed_property)
        )
        assert observed_property_get.name == message
        assert ObservedPropertyGetResponse.from_orm(observed_property_get)


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
def test_create_observed_property(get_user, user, workspace, message, error_code):
    observed_property_data = ObservedPropertyPostBody(
        name="New",
        code="New",
        description="New",
        definition="New",
        observed_property_type="New",
        workspace_id=uuid.UUID(workspace),
    )
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            observed_property_service.create(
                user=get_user(user), data=observed_property_data
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        observed_property_create = observed_property_service.create(
            user=get_user(user), data=observed_property_data
        )
        assert observed_property_create.name == observed_property_data.name
        assert (
            observed_property_create.description == observed_property_data.description
        )
        assert observed_property_create.definition == observed_property_data.definition
        assert observed_property_create.code == observed_property_data.code
        assert (
            observed_property_create.observed_property_type
            == observed_property_data.observed_property_type
        )
        assert (
            observed_property_create.description == observed_property_data.description
        )
        assert (
            observed_property_create.workspace_id == observed_property_data.workspace_id
        )
        assert ObservedPropertyGetResponse.from_orm(observed_property_create)


@pytest.mark.parametrize(
    "user, observed_property, message, error_code",
    [
        (
            "owner",
            "49a245bd-4517-4dea-b3ba-25c919bf2cf5",
            "You do not have permission",
            403,
        ),
        ("owner", "cac1262e-68ee-43a0-9222-f214f2161091", None, None),
        ("owner", "5dbfd184-ae79-4c05-a9ea-3f5e775ecbc1", None, None),
        ("admin", "49a245bd-4517-4dea-b3ba-25c919bf2cf5", None, None),
        ("admin", "cac1262e-68ee-43a0-9222-f214f2161091", None, None),
        ("admin", "5dbfd184-ae79-4c05-a9ea-3f5e775ecbc1", None, None),
        (
            "editor",
            "49a245bd-4517-4dea-b3ba-25c919bf2cf5",
            "You do not have permission",
            403,
        ),
        ("editor", "cac1262e-68ee-43a0-9222-f214f2161091", None, None),
        ("editor", "5dbfd184-ae79-4c05-a9ea-3f5e775ecbc1", None, None),
        (
            "viewer",
            "49a245bd-4517-4dea-b3ba-25c919bf2cf5",
            "You do not have permission",
            403,
        ),
        (
            "viewer",
            "cac1262e-68ee-43a0-9222-f214f2161091",
            "You do not have permission",
            403,
        ),
        (
            "viewer",
            "5dbfd184-ae79-4c05-a9ea-3f5e775ecbc1",
            "You do not have permission",
            403,
        ),
        (
            "anonymous",
            "49a245bd-4517-4dea-b3ba-25c919bf2cf5",
            "You do not have permission",
            403,
        ),
        (
            "anonymous",
            "cac1262e-68ee-43a0-9222-f214f2161091",
            "You do not have permission",
            403,
        ),
        (
            "anonymous",
            "5dbfd184-ae79-4c05-a9ea-3f5e775ecbc1",
            "Observed property does not exist",
            404,
        ),
        (
            "anonymous",
            "00000000-0000-0000-0000-000000000000",
            "Observed property does not exist",
            404,
        ),
        (
            None,
            "49a245bd-4517-4dea-b3ba-25c919bf2cf5",
            "You do not have permission",
            403,
        ),
        (
            None,
            "cac1262e-68ee-43a0-9222-f214f2161091",
            "You do not have permission",
            403,
        ),
        (
            None,
            "5dbfd184-ae79-4c05-a9ea-3f5e775ecbc1",
            "Observed property does not exist",
            404,
        ),
        (
            None,
            "00000000-0000-0000-0000-000000000000",
            "Observed property does not exist",
            404,
        ),
    ],
)
def test_edit_observed_property(get_user, user, observed_property, message, error_code):
    observed_property_data = ObservedPropertyPatchBody(
        name="New",
        code="New",
        description="New",
        definition="New",
        observed_property_type="New",
    )
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            observed_property_service.update(
                user=get_user(user),
                uid=uuid.UUID(observed_property),
                data=observed_property_data,
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        observed_property_update = observed_property_service.update(
            user=get_user(user),
            uid=uuid.UUID(observed_property),
            data=observed_property_data,
        )
        assert observed_property_update.name == observed_property_data.name
        assert (
            observed_property_update.description == observed_property_data.description
        )
        assert observed_property_update.definition == observed_property_data.definition
        assert observed_property_update.code == observed_property_data.code
        assert (
            observed_property_update.observed_property_type
            == observed_property_data.observed_property_type
        )
        assert (
            observed_property_update.description == observed_property_data.description
        )
        assert ObservedPropertyGetResponse.from_orm(observed_property_update)


@pytest.mark.parametrize(
    "user, observed_property, message, error_code",
    [
        (
            "owner",
            "49a245bd-4517-4dea-b3ba-25c919bf2cf5",
            "You do not have permission",
            403,
        ),
        ("owner", "cac1262e-68ee-43a0-9222-f214f2161091", None, None),
        ("owner", "5dbfd184-ae79-4c05-a9ea-3f5e775ecbc1", None, None),
        ("admin", "49a245bd-4517-4dea-b3ba-25c919bf2cf5", None, None),
        ("admin", "cac1262e-68ee-43a0-9222-f214f2161091", None, None),
        ("admin", "5dbfd184-ae79-4c05-a9ea-3f5e775ecbc1", None, None),
        (
            "admin",
            "a5746e4e-f479-4476-a462-6a8f7874794d",
            "Observed property in use by one or more datastreams",
            409,
        ),
        (
            "editor",
            "49a245bd-4517-4dea-b3ba-25c919bf2cf5",
            "You do not have permission",
            403,
        ),
        ("editor", "cac1262e-68ee-43a0-9222-f214f2161091", None, None),
        ("editor", "5dbfd184-ae79-4c05-a9ea-3f5e775ecbc1", None, None),
        (
            "viewer",
            "49a245bd-4517-4dea-b3ba-25c919bf2cf5",
            "You do not have permission",
            403,
        ),
        (
            "viewer",
            "cac1262e-68ee-43a0-9222-f214f2161091",
            "You do not have permission",
            403,
        ),
        (
            "viewer",
            "5dbfd184-ae79-4c05-a9ea-3f5e775ecbc1",
            "You do not have permission",
            403,
        ),
        (
            "anonymous",
            "49a245bd-4517-4dea-b3ba-25c919bf2cf5",
            "You do not have permission",
            403,
        ),
        (
            "anonymous",
            "cac1262e-68ee-43a0-9222-f214f2161091",
            "You do not have permission",
            403,
        ),
        (
            "anonymous",
            "5dbfd184-ae79-4c05-a9ea-3f5e775ecbc1",
            "Observed property does not exist",
            404,
        ),
        (
            "anonymous",
            "00000000-0000-0000-0000-000000000000",
            "Observed property does not exist",
            404,
        ),
        (
            None,
            "49a245bd-4517-4dea-b3ba-25c919bf2cf5",
            "You do not have permission",
            403,
        ),
        (
            None,
            "cac1262e-68ee-43a0-9222-f214f2161091",
            "You do not have permission",
            403,
        ),
        (
            None,
            "5dbfd184-ae79-4c05-a9ea-3f5e775ecbc1",
            "Observed property does not exist",
            404,
        ),
        (
            None,
            "00000000-0000-0000-0000-000000000000",
            "Observed property does not exist",
            404,
        ),
    ],
)
def test_delete_observed_property(
    get_user, user, observed_property, message, error_code
):
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            observed_property_service.delete(
                user=get_user(user), uid=uuid.UUID(observed_property)
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        observed_property_delete = observed_property_service.delete(
            user=get_user(user), uid=uuid.UUID(observed_property)
        )
        assert observed_property_delete == "Observed property deleted"
