import pytest
import uuid
from ninja.errors import HttpError
from sta.services import SensorService
from sta.schemas import SensorPostBody, SensorPatchBody, SensorGetResponse

sensor_service = SensorService()


@pytest.mark.parametrize(
    "principal, workspace, length, max_queries",
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
        ("apikey", None, 4, 3),
        ("apikey", "6e0deaf2-a92b-421b-9ece-86783265596f", 2, 3),
        ("apikey", "b27c51a0-7374-462d-8a53-d97d47176c10", 0, 3),
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
def test_list_sensor(
    django_assert_num_queries, get_principal, principal, workspace, length, max_queries
):
    with django_assert_num_queries(max_queries):
        sensor_list = sensor_service.list(
            principal=get_principal(principal),
            workspace_id=uuid.UUID(workspace) if workspace else None,
        )
        assert len(sensor_list) == length
        assert (SensorGetResponse.from_orm(sensor) for sensor in sensor_list)


@pytest.mark.parametrize(
    "principal, sensor, message, error_code",
    [
        ("owner", "a947c551-8e21-4848-a89b-3048aec69574", "System Sensor", None),
        ("owner", "f87072e1-6ccb-46ec-ab34-befb453140de", "Public Sensor", None),
        ("owner", "89a6ae16-9f85-4279-985e-83484db47107", "Private Sensor", None),
        ("admin", "a947c551-8e21-4848-a89b-3048aec69574", "System Sensor", None),
        ("admin", "f87072e1-6ccb-46ec-ab34-befb453140de", "Public Sensor", None),
        ("admin", "89a6ae16-9f85-4279-985e-83484db47107", "Private Sensor", None),
        ("editor", "a947c551-8e21-4848-a89b-3048aec69574", "System Sensor", None),
        ("editor", "f87072e1-6ccb-46ec-ab34-befb453140de", "Public Sensor", None),
        ("editor", "89a6ae16-9f85-4279-985e-83484db47107", "Private Sensor", None),
        ("viewer", "a947c551-8e21-4848-a89b-3048aec69574", "System Sensor", None),
        ("viewer", "f87072e1-6ccb-46ec-ab34-befb453140de", "Public Sensor", None),
        ("viewer", "89a6ae16-9f85-4279-985e-83484db47107", "Private Sensor", None),
        ("apikey", "a947c551-8e21-4848-a89b-3048aec69574", "System Sensor", None),
        ("apikey", "f87072e1-6ccb-46ec-ab34-befb453140de", "Public Sensor", None),
        (
            "apikey",
            "89a6ae16-9f85-4279-985e-83484db47107",
            "Sensor does not exist",
            404,
        ),
        ("anonymous", "a947c551-8e21-4848-a89b-3048aec69574", "System Sensor", None),
        ("anonymous", "f87072e1-6ccb-46ec-ab34-befb453140de", "Public Sensor", None),
        (
            "anonymous",
            "89a6ae16-9f85-4279-985e-83484db47107",
            "Sensor does not exist",
            404,
        ),
        (
            "anonymous",
            "00000000-0000-0000-0000-000000000000",
            "Sensor does not exist",
            404,
        ),
        (None, "a947c551-8e21-4848-a89b-3048aec69574", "System Sensor", None),
        (None, "f87072e1-6ccb-46ec-ab34-befb453140de", "Public Sensor", None),
        (
            None,
            "89a6ae16-9f85-4279-985e-83484db47107",
            "Sensor does not exist",
            404,
        ),
        (
            None,
            "00000000-0000-0000-0000-000000000000",
            "Sensor does not exist",
            404,
        ),
    ],
)
def test_get_sensor(get_principal, principal, sensor, message, error_code):
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            sensor_service.get(
                principal=get_principal(principal), uid=uuid.UUID(sensor)
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        sensor_get = sensor_service.get(
            principal=get_principal(principal), uid=uuid.UUID(sensor)
        )
        assert sensor_get.name == message
        assert SensorGetResponse.from_orm(sensor_get)


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
def test_create_sensor(get_principal, principal, workspace, message, error_code):
    sensor_data = SensorPostBody(
        name="New",
        description="New",
        encoding_type="application/json",
        method_type="New",
        workspace_id=uuid.UUID(workspace),
    )
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            sensor_service.create(principal=get_principal(principal), data=sensor_data)
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        sensor_create = sensor_service.create(
            principal=get_principal(principal), data=sensor_data
        )
        assert sensor_create.description == sensor_data.description
        assert sensor_create.name == sensor_data.name
        assert sensor_create.encoding_type == sensor_data.encoding_type
        assert sensor_create.method_type == sensor_data.method_type
        assert SensorGetResponse.from_orm(sensor_create)


@pytest.mark.parametrize(
    "principal, sensor, message, error_code",
    [
        (
            "owner",
            "a947c551-8e21-4848-a89b-3048aec69574",
            "You do not have permission",
            403,
        ),
        ("owner", "f87072e1-6ccb-46ec-ab34-befb453140de", None, None),
        ("owner", "89a6ae16-9f85-4279-985e-83484db47107", None, None),
        ("admin", "a947c551-8e21-4848-a89b-3048aec69574", None, None),
        ("admin", "f87072e1-6ccb-46ec-ab34-befb453140de", None, None),
        ("admin", "89a6ae16-9f85-4279-985e-83484db47107", None, None),
        (
            "editor",
            "a947c551-8e21-4848-a89b-3048aec69574",
            "You do not have permission",
            403,
        ),
        ("editor", "f87072e1-6ccb-46ec-ab34-befb453140de", None, None),
        ("editor", "89a6ae16-9f85-4279-985e-83484db47107", None, None),
        (
            "viewer",
            "a947c551-8e21-4848-a89b-3048aec69574",
            "You do not have permission",
            403,
        ),
        (
            "viewer",
            "f87072e1-6ccb-46ec-ab34-befb453140de",
            "You do not have permission",
            403,
        ),
        (
            "viewer",
            "89a6ae16-9f85-4279-985e-83484db47107",
            "You do not have permission",
            403,
        ),
        (
            "apikey",
            "a947c551-8e21-4848-a89b-3048aec69574",
            "You do not have permission",
            403,
        ),
        (
            "apikey",
            "f87072e1-6ccb-46ec-ab34-befb453140de",
            "You do not have permission",
            403,
        ),
        (
            "apikey",
            "89a6ae16-9f85-4279-985e-83484db47107",
            "Sensor does not exist",
            404,
        ),
        (
            "anonymous",
            "a947c551-8e21-4848-a89b-3048aec69574",
            "You do not have permission",
            403,
        ),
        (
            "anonymous",
            "f87072e1-6ccb-46ec-ab34-befb453140de",
            "You do not have permission",
            403,
        ),
        (
            "anonymous",
            "89a6ae16-9f85-4279-985e-83484db47107",
            "Sensor does not exist",
            404,
        ),
        (
            "anonymous",
            "00000000-0000-0000-0000-000000000000",
            "Sensor does not exist",
            404,
        ),
        (
            None,
            "a947c551-8e21-4848-a89b-3048aec69574",
            "You do not have permission",
            403,
        ),
        (
            None,
            "f87072e1-6ccb-46ec-ab34-befb453140de",
            "You do not have permission",
            403,
        ),
        (
            None,
            "89a6ae16-9f85-4279-985e-83484db47107",
            "Sensor does not exist",
            404,
        ),
        (
            None,
            "00000000-0000-0000-0000-000000000000",
            "Sensor does not exist",
            404,
        ),
    ],
)
def test_edit_sensor(get_principal, principal, sensor, message, error_code):
    sensor_data = SensorPatchBody(
        name="New",
        description="New",
        encoding_type="application/json",
        method_type="New",
    )
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            sensor_service.update(
                principal=get_principal(principal),
                uid=uuid.UUID(sensor),
                data=sensor_data,
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        sensor_update = sensor_service.update(
            principal=get_principal(principal), uid=uuid.UUID(sensor), data=sensor_data
        )
        assert sensor_update.description == sensor_data.description
        assert sensor_update.name == sensor_data.name
        assert sensor_update.encoding_type == sensor_data.encoding_type
        assert sensor_update.method_type == sensor_data.method_type
        assert SensorGetResponse.from_orm(sensor_update)


@pytest.mark.parametrize(
    "principal, sensor, message, error_code",
    [
        (
            "owner",
            "a947c551-8e21-4848-a89b-3048aec69574",
            "You do not have permission",
            403,
        ),
        ("owner", "f87072e1-6ccb-46ec-ab34-befb453140de", None, None),
        ("owner", "89a6ae16-9f85-4279-985e-83484db47107", None, None),
        ("admin", "a947c551-8e21-4848-a89b-3048aec69574", None, None),
        ("admin", "f87072e1-6ccb-46ec-ab34-befb453140de", None, None),
        ("admin", "89a6ae16-9f85-4279-985e-83484db47107", None, None),
        (
            "admin",
            "291625d8-0f6e-46d6-918c-6c3af3d345ab",
            "Sensor in use by one or more datastreams",
            409,
        ),
        (
            "editor",
            "a947c551-8e21-4848-a89b-3048aec69574",
            "You do not have permission",
            403,
        ),
        ("editor", "f87072e1-6ccb-46ec-ab34-befb453140de", None, None),
        ("editor", "89a6ae16-9f85-4279-985e-83484db47107", None, None),
        (
            "viewer",
            "a947c551-8e21-4848-a89b-3048aec69574",
            "You do not have permission",
            403,
        ),
        (
            "viewer",
            "f87072e1-6ccb-46ec-ab34-befb453140de",
            "You do not have permission",
            403,
        ),
        (
            "viewer",
            "89a6ae16-9f85-4279-985e-83484db47107",
            "You do not have permission",
            403,
        ),
        (
            "apikey",
            "a947c551-8e21-4848-a89b-3048aec69574",
            "You do not have permission",
            403,
        ),
        (
            "apikey",
            "f87072e1-6ccb-46ec-ab34-befb453140de",
            "You do not have permission",
            403,
        ),
        (
            "apikey",
            "89a6ae16-9f85-4279-985e-83484db47107",
            "Sensor does not exist",
            404,
        ),
        (
            "anonymous",
            "a947c551-8e21-4848-a89b-3048aec69574",
            "You do not have permission",
            403,
        ),
        (
            "anonymous",
            "f87072e1-6ccb-46ec-ab34-befb453140de",
            "You do not have permission",
            403,
        ),
        (
            "anonymous",
            "89a6ae16-9f85-4279-985e-83484db47107",
            "Sensor does not exist",
            404,
        ),
        (
            "anonymous",
            "00000000-0000-0000-0000-000000000000",
            "Sensor does not exist",
            404,
        ),
        (
            None,
            "a947c551-8e21-4848-a89b-3048aec69574",
            "You do not have permission",
            403,
        ),
        (
            None,
            "f87072e1-6ccb-46ec-ab34-befb453140de",
            "You do not have permission",
            403,
        ),
        (
            None,
            "89a6ae16-9f85-4279-985e-83484db47107",
            "Sensor does not exist",
            404,
        ),
        (
            None,
            "00000000-0000-0000-0000-000000000000",
            "Sensor does not exist",
            404,
        ),
    ],
)
def test_delete_sensor(get_principal, principal, sensor, message, error_code):
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            sensor_service.delete(
                principal=get_principal(principal), uid=uuid.UUID(sensor)
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        sensor_delete = sensor_service.delete(
            principal=get_principal(principal), uid=uuid.UUID(sensor)
        )
        assert sensor_delete == "Sensor deleted"
