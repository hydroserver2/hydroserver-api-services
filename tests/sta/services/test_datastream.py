import pytest
import uuid
from ninja.errors import HttpError
from sta.services import DatastreamService
from sta.schemas import DatastreamPostBody, DatastreamPatchBody, DatastreamGetResponse

datastream_service = DatastreamService()


@pytest.mark.parametrize("user, workspace, thing, length, max_queries", [
    # Owners can filter datastreams by thing and workspace
    ("owner", None, None, 9, 2),
    ("owner", "6e0deaf2-a92b-421b-9ece-86783265596f", None, 5, 2),
    ("owner", "6e0deaf2-a92b-421b-9ece-86783265596f", "3b7818af-eff7-4149-8517-e5cad9dc22e1", 3, 2),
    ("owner", "b27c51a0-7374-462d-8a53-d97d47176c10", None, 4, 2),
    ("owner", "b27c51a0-7374-462d-8a53-d97d47176c10", "76dadda5-224b-4e1f-8570-e385bd482b2d", 2, 2),
    ("owner", "b27c51a0-7374-462d-8a53-d97d47176c10", "3b7818af-eff7-4149-8517-e5cad9dc22e1", 0, 2),

    # Admins can filter datastreams by thing and workspace
    ("admin", None, None, 9, 2),
    ("admin", "6e0deaf2-a92b-421b-9ece-86783265596f", None, 5, 2),
    ("admin", "6e0deaf2-a92b-421b-9ece-86783265596f", "3b7818af-eff7-4149-8517-e5cad9dc22e1", 3, 2),
    ("admin", "b27c51a0-7374-462d-8a53-d97d47176c10", None, 4, 2),
    ("admin", "b27c51a0-7374-462d-8a53-d97d47176c10", "76dadda5-224b-4e1f-8570-e385bd482b2d", 2, 2),
    ("admin", "b27c51a0-7374-462d-8a53-d97d47176c10", "3b7818af-eff7-4149-8517-e5cad9dc22e1", 0, 2),

    # Editors can filter datastreams by thing and workspace
    ("editor", None, None, 9, 2),
    ("editor", "6e0deaf2-a92b-421b-9ece-86783265596f", None, 5, 2),
    ("editor", "6e0deaf2-a92b-421b-9ece-86783265596f", "3b7818af-eff7-4149-8517-e5cad9dc22e1", 3, 2),
    ("editor", "b27c51a0-7374-462d-8a53-d97d47176c10", None, 4, 2),
    ("editor", "b27c51a0-7374-462d-8a53-d97d47176c10", "76dadda5-224b-4e1f-8570-e385bd482b2d", 2, 2),
    ("editor", "b27c51a0-7374-462d-8a53-d97d47176c10", "3b7818af-eff7-4149-8517-e5cad9dc22e1", 0, 2),

    # Viewers can filter datastreams by thing and workspace
    ("viewer", None, None, 9, 2),
    ("viewer", "6e0deaf2-a92b-421b-9ece-86783265596f", None, 5, 2),
    ("viewer", "6e0deaf2-a92b-421b-9ece-86783265596f", "3b7818af-eff7-4149-8517-e5cad9dc22e1", 3, 2),
    ("viewer", "b27c51a0-7374-462d-8a53-d97d47176c10", None, 4, 2),
    ("viewer", "b27c51a0-7374-462d-8a53-d97d47176c10", "76dadda5-224b-4e1f-8570-e385bd482b2d", 2, 2),
    ("viewer", "b27c51a0-7374-462d-8a53-d97d47176c10", "3b7818af-eff7-4149-8517-e5cad9dc22e1", 0, 2),

    # Anonymous can filter datastreams by thing and workspace
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
    # Owners, admins, editors, and viewers can get public and private datastreams
    ("owner", "27c70b41-e845-40ea-8cc7-d1b40f89816b", "Public Datastream 1", None),
    ("owner", "9f96957b-ee20-4c7b-bf2b-673a0cda3a04", "Private Datastream 7", None),
    ("admin", "27c70b41-e845-40ea-8cc7-d1b40f89816b", "Public Datastream 1", None),
    ("admin", "9f96957b-ee20-4c7b-bf2b-673a0cda3a04", "Private Datastream 7", None),
    ("editor", "27c70b41-e845-40ea-8cc7-d1b40f89816b", "Public Datastream 1", None),
    ("editor", "9f96957b-ee20-4c7b-bf2b-673a0cda3a04", "Private Datastream 7", None),
    ("viewer", "27c70b41-e845-40ea-8cc7-d1b40f89816b", "Public Datastream 1", None),
    ("viewer", "9f96957b-ee20-4c7b-bf2b-673a0cda3a04", "Private Datastream 7", None),

    # Anonymous can get public but not private or non-existent datastreams
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
        assert DatastreamGetResponse.from_orm(datastream_get)


@pytest.mark.parametrize("user, thing, observed_property, processing_level, sensor, unit, message, error_code", [
    # Owner can create datastream with system metadata
    ("owner", "3b7818af-eff7-4149-8517-e5cad9dc22e1", "49a245bd-4517-4dea-b3ba-25c919bf2cf5",
     "1cb782af-6097-4a3f-9988-5fcbfcb5a327", "a947c551-8e21-4848-a89b-3048aec69574",
     "2ca850fa-ce19-4d8a-9dfd-8d54a261778d", None, None),

    # Owner can create datastream with workspace metadata
    ("owner", "3b7818af-eff7-4149-8517-e5cad9dc22e1", "cac1262e-68ee-43a0-9222-f214f2161091",
     "aa2d8fa4-461f-48a4-8bfe-13b6ae6fa575", "f87072e1-6ccb-46ec-ab34-befb453140de",
     "fe3799b7-f061-42f2-b012-b569303f8a41", None, None),

    # Owner can't create datastream with metadata from another workspace
    ("owner", "3b7818af-eff7-4149-8517-e5cad9dc22e1", "5dbfd184-ae79-4c05-a9ea-3f5e775ecbc1",
     "aa2d8fa4-461f-48a4-8bfe-13b6ae6fa575", "f87072e1-6ccb-46ec-ab34-befb453140de",
     "fe3799b7-f061-42f2-b012-b569303f8a41", "The given observed property cannot be associated", 400),
    ("owner", "3b7818af-eff7-4149-8517-e5cad9dc22e1", "cac1262e-68ee-43a0-9222-f214f2161091",
     "fa3c97ce-41b8-4c12-b91a-9127ce0c083a", "f87072e1-6ccb-46ec-ab34-befb453140de",
     "fe3799b7-f061-42f2-b012-b569303f8a41", "The given processing level cannot be associated", 400),
    ("owner", "3b7818af-eff7-4149-8517-e5cad9dc22e1", "cac1262e-68ee-43a0-9222-f214f2161091",
     "aa2d8fa4-461f-48a4-8bfe-13b6ae6fa575", "89a6ae16-9f85-4279-985e-83484db47107",
     "fe3799b7-f061-42f2-b012-b569303f8a41", "The given sensor cannot be associated", 400),
    ("owner", "3b7818af-eff7-4149-8517-e5cad9dc22e1", "cac1262e-68ee-43a0-9222-f214f2161091",
     "aa2d8fa4-461f-48a4-8bfe-13b6ae6fa575", "f87072e1-6ccb-46ec-ab34-befb453140de",
     "98a74429-2be2-44c0-8f7f-2df2ca12893d", "The given unit cannot be associated", 400),

    # Owner can't create datastream with non-existent metadata
    ("owner", "00000000-0000-0000-0000-000000000000", "cac1262e-68ee-43a0-9222-f214f2161091",
     "aa2d8fa4-461f-48a4-8bfe-13b6ae6fa575", "f87072e1-6ccb-46ec-ab34-befb453140de",
     "fe3799b7-f061-42f2-b012-b569303f8a41", "Thing does not exist", 400),
    ("owner", "3b7818af-eff7-4149-8517-e5cad9dc22e1", "00000000-0000-0000-0000-000000000000",
     "aa2d8fa4-461f-48a4-8bfe-13b6ae6fa575", "f87072e1-6ccb-46ec-ab34-befb453140de",
     "fe3799b7-f061-42f2-b012-b569303f8a41", "Observed property does not exist", 400),
    ("owner", "3b7818af-eff7-4149-8517-e5cad9dc22e1", "cac1262e-68ee-43a0-9222-f214f2161091",
     "00000000-0000-0000-0000-000000000000", "f87072e1-6ccb-46ec-ab34-befb453140de",
     "fe3799b7-f061-42f2-b012-b569303f8a41", "Processing level does not exist", 400),
    ("owner", "3b7818af-eff7-4149-8517-e5cad9dc22e1", "cac1262e-68ee-43a0-9222-f214f2161091",
     "aa2d8fa4-461f-48a4-8bfe-13b6ae6fa575", "00000000-0000-0000-0000-000000000000",
     "fe3799b7-f061-42f2-b012-b569303f8a41", "Sensor does not exist", 400),
    ("owner", "3b7818af-eff7-4149-8517-e5cad9dc22e1", "cac1262e-68ee-43a0-9222-f214f2161091",
     "aa2d8fa4-461f-48a4-8bfe-13b6ae6fa575", "f87072e1-6ccb-46ec-ab34-befb453140de",
     "00000000-0000-0000-0000-000000000000", "Unit does not exist", 400),

    # Admin can create datastream with system metadata
    ("admin", "3b7818af-eff7-4149-8517-e5cad9dc22e1", "49a245bd-4517-4dea-b3ba-25c919bf2cf5",
     "1cb782af-6097-4a3f-9988-5fcbfcb5a327", "a947c551-8e21-4848-a89b-3048aec69574",
     "2ca850fa-ce19-4d8a-9dfd-8d54a261778d", None, None),

    # Admin can create datastream with workspace metadata
    ("admin", "3b7818af-eff7-4149-8517-e5cad9dc22e1", "cac1262e-68ee-43a0-9222-f214f2161091",
     "aa2d8fa4-461f-48a4-8bfe-13b6ae6fa575", "f87072e1-6ccb-46ec-ab34-befb453140de",
     "fe3799b7-f061-42f2-b012-b569303f8a41", None, None),

    # Admin can't create datastream with metadata from another workspace
    ("admin", "3b7818af-eff7-4149-8517-e5cad9dc22e1", "5dbfd184-ae79-4c05-a9ea-3f5e775ecbc1",
     "aa2d8fa4-461f-48a4-8bfe-13b6ae6fa575", "f87072e1-6ccb-46ec-ab34-befb453140de",
     "fe3799b7-f061-42f2-b012-b569303f8a41", "The given observed property cannot be associated", 400),
    ("admin", "3b7818af-eff7-4149-8517-e5cad9dc22e1", "cac1262e-68ee-43a0-9222-f214f2161091",
     "fa3c97ce-41b8-4c12-b91a-9127ce0c083a", "f87072e1-6ccb-46ec-ab34-befb453140de",
     "fe3799b7-f061-42f2-b012-b569303f8a41", "The given processing level cannot be associated", 400),
    ("admin", "3b7818af-eff7-4149-8517-e5cad9dc22e1", "cac1262e-68ee-43a0-9222-f214f2161091",
     "aa2d8fa4-461f-48a4-8bfe-13b6ae6fa575", "89a6ae16-9f85-4279-985e-83484db47107",
     "fe3799b7-f061-42f2-b012-b569303f8a41", "The given sensor cannot be associated", 400),
    ("admin", "3b7818af-eff7-4149-8517-e5cad9dc22e1", "cac1262e-68ee-43a0-9222-f214f2161091",
     "aa2d8fa4-461f-48a4-8bfe-13b6ae6fa575", "f87072e1-6ccb-46ec-ab34-befb453140de",
     "98a74429-2be2-44c0-8f7f-2df2ca12893d", "The given unit cannot be associated", 400),

    # Admin can't create datastream with non-existent metadata
    ("admin", "00000000-0000-0000-0000-000000000000", "cac1262e-68ee-43a0-9222-f214f2161091",
     "aa2d8fa4-461f-48a4-8bfe-13b6ae6fa575", "f87072e1-6ccb-46ec-ab34-befb453140de",
     "fe3799b7-f061-42f2-b012-b569303f8a41", "Thing does not exist", 400),
    ("admin", "3b7818af-eff7-4149-8517-e5cad9dc22e1", "00000000-0000-0000-0000-000000000000",
     "aa2d8fa4-461f-48a4-8bfe-13b6ae6fa575", "f87072e1-6ccb-46ec-ab34-befb453140de",
     "fe3799b7-f061-42f2-b012-b569303f8a41", "Observed property does not exist", 400),
    ("admin", "3b7818af-eff7-4149-8517-e5cad9dc22e1", "cac1262e-68ee-43a0-9222-f214f2161091",
     "00000000-0000-0000-0000-000000000000", "f87072e1-6ccb-46ec-ab34-befb453140de",
     "fe3799b7-f061-42f2-b012-b569303f8a41", "Processing level does not exist", 400),
    ("admin", "3b7818af-eff7-4149-8517-e5cad9dc22e1", "cac1262e-68ee-43a0-9222-f214f2161091",
     "aa2d8fa4-461f-48a4-8bfe-13b6ae6fa575", "00000000-0000-0000-0000-000000000000",
     "fe3799b7-f061-42f2-b012-b569303f8a41", "Sensor does not exist", 400),
    ("admin", "3b7818af-eff7-4149-8517-e5cad9dc22e1", "cac1262e-68ee-43a0-9222-f214f2161091",
     "aa2d8fa4-461f-48a4-8bfe-13b6ae6fa575", "f87072e1-6ccb-46ec-ab34-befb453140de",
     "00000000-0000-0000-0000-000000000000", "Unit does not exist", 400),

    # Editor can create datastream with system metadata
    ("editor", "3b7818af-eff7-4149-8517-e5cad9dc22e1", "49a245bd-4517-4dea-b3ba-25c919bf2cf5",
     "1cb782af-6097-4a3f-9988-5fcbfcb5a327", "a947c551-8e21-4848-a89b-3048aec69574",
     "2ca850fa-ce19-4d8a-9dfd-8d54a261778d", None, None),
    # Editor can create datastream with workspace metadata
    ("editor", "3b7818af-eff7-4149-8517-e5cad9dc22e1", "cac1262e-68ee-43a0-9222-f214f2161091",
     "aa2d8fa4-461f-48a4-8bfe-13b6ae6fa575", "f87072e1-6ccb-46ec-ab34-befb453140de",
     "fe3799b7-f061-42f2-b012-b569303f8a41", None, None),

    # Viewer cannot create datastreams
    ("viewer", "3b7818af-eff7-4149-8517-e5cad9dc22e1", "49a245bd-4517-4dea-b3ba-25c919bf2cf5",
     "1cb782af-6097-4a3f-9988-5fcbfcb5a327", "a947c551-8e21-4848-a89b-3048aec69574",
     "2ca850fa-ce19-4d8a-9dfd-8d54a261778d", "You do not have permission", 403),
    ("viewer", "76dadda5-224b-4e1f-8570-e385bd482b2d", "49a245bd-4517-4dea-b3ba-25c919bf2cf5",
     "1cb782af-6097-4a3f-9988-5fcbfcb5a327", "a947c551-8e21-4848-a89b-3048aec69574",
     "2ca850fa-ce19-4d8a-9dfd-8d54a261778d", "You do not have permission", 403),

    # Anonymous cannot create datastreams
    ("anonymous", "3b7818af-eff7-4149-8517-e5cad9dc22e1", "49a245bd-4517-4dea-b3ba-25c919bf2cf5",
     "1cb782af-6097-4a3f-9988-5fcbfcb5a327", "a947c551-8e21-4848-a89b-3048aec69574",
     "2ca850fa-ce19-4d8a-9dfd-8d54a261778d", "You do not have permission", 403),
    ("anonymous", "76dadda5-224b-4e1f-8570-e385bd482b2d", "49a245bd-4517-4dea-b3ba-25c919bf2cf5",
     "1cb782af-6097-4a3f-9988-5fcbfcb5a327", "a947c551-8e21-4848-a89b-3048aec69574",
     "2ca850fa-ce19-4d8a-9dfd-8d54a261778d", "Thing does not exist", 400),
    ("anonymous", "92a3a099-f2d3-40ec-9b0e-d25ae8bf59b7", "49a245bd-4517-4dea-b3ba-25c919bf2cf5",
     "1cb782af-6097-4a3f-9988-5fcbfcb5a327", "a947c551-8e21-4848-a89b-3048aec69574",
     "2ca850fa-ce19-4d8a-9dfd-8d54a261778d", "Thing does not exist", 400),
    ("anonymous", "819260c8-2543-4046-b8c4-7431243ed7c5", "49a245bd-4517-4dea-b3ba-25c919bf2cf5",
     "1cb782af-6097-4a3f-9988-5fcbfcb5a327", "a947c551-8e21-4848-a89b-3048aec69574",
     "2ca850fa-ce19-4d8a-9dfd-8d54a261778d", "Thing does not exist", 400),
    ("anonymous", "00000000-0000-0000-0000-000000000000", "49a245bd-4517-4dea-b3ba-25c919bf2cf5",
     "1cb782af-6097-4a3f-9988-5fcbfcb5a327", "a947c551-8e21-4848-a89b-3048aec69574",
     "2ca850fa-ce19-4d8a-9dfd-8d54a261778d", "Thing does not exist", 400),
])
def test_create_datastream(get_user, user, thing, observed_property, processing_level, sensor, unit, message,
                           error_code):
    datastream_data = DatastreamPostBody(
        thing_id=uuid.UUID(thing), observed_property_id=uuid.UUID(observed_property),
        processing_level_id=uuid.UUID(processing_level), sensor_id=uuid.UUID(sensor), unit_id=uuid.UUID(unit),
        name="New Datastream", description="New Datastream", observation_type="Observation", sampled_medium="Air",
        no_data_value=-9999, aggregation_statistic="Average", time_aggregation_interval=15,
        time_aggregation_interval_unit="minutes", result_type="Time Series"
    )
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            datastream_service.create(
                user=get_user(user), data=datastream_data
            )
        assert exc_info.value.status_code == error_code
        if isinstance(message, str):
            assert exc_info.value.message.startswith(message)
    else:
        datastream_create = datastream_service.create(
            user=get_user(user), data=datastream_data
        )
        assert datastream_create.name == datastream_data.name
        assert datastream_create.description == datastream_data.description
        assert datastream_create.observed_property_id == datastream_data.observed_property_id
        assert datastream_create.processing_level_id == datastream_data.processing_level_id
        assert datastream_create.sensor_id == datastream_data.sensor_id
        assert datastream_create.unit_id == datastream_data.unit_id
        assert datastream_create.observation_type == datastream_data.observation_type
        assert datastream_create.time_aggregation_interval == datastream_data.time_aggregation_interval
        assert datastream_create.sampled_medium == datastream_data.sampled_medium
        assert datastream_create.no_data_value == datastream_data.no_data_value
        assert datastream_create.aggregation_statistic == datastream_data.aggregation_statistic
        assert datastream_create.time_aggregation_interval == datastream_data.time_aggregation_interval
        assert datastream_create.time_aggregation_interval_unit == datastream_data.time_aggregation_interval_unit
        assert datastream_create.result_type == datastream_data.result_type
        assert DatastreamGetResponse.from_orm(datastream_create)


@pytest.mark.parametrize(
    "user, datastream, thing, observed_property, processing_level, sensor, unit, message, error_code", [
        # Owners, editors, and admins can assign system and workspace metadata to public and private datastreams
        ("owner", "27c70b41-e845-40ea-8cc7-d1b40f89816b", None, None, None, None, None, None, None),
        ("owner", "27c70b41-e845-40ea-8cc7-d1b40f89816b", None, None, None, None, None, None, None),
        ("owner", "9f96957b-ee20-4c7b-bf2b-673a0cda3a04", None, None, None, None, None, None, None),
        ("owner", "9f96957b-ee20-4c7b-bf2b-673a0cda3a04", None, None, None, None, None, None, None),
        ("admin", "27c70b41-e845-40ea-8cc7-d1b40f89816b", None, None, None, None, None, None, None),
        ("admin", "27c70b41-e845-40ea-8cc7-d1b40f89816b", None, None, None, None, None, None, None),
        ("admin", "9f96957b-ee20-4c7b-bf2b-673a0cda3a04", None, None, None, None, None, None, None),
        ("admin", "9f96957b-ee20-4c7b-bf2b-673a0cda3a04", None, None, None, None, None, None, None),
        ("editor", "27c70b41-e845-40ea-8cc7-d1b40f89816b", None, None, None, None, None, None, None),
        ("editor", "27c70b41-e845-40ea-8cc7-d1b40f89816b", None, None, None, None, None, None, None),
        ("editor", "9f96957b-ee20-4c7b-bf2b-673a0cda3a04", None, None, None, None, None, None, None),
        ("editor", "9f96957b-ee20-4c7b-bf2b-673a0cda3a04", None, None, None, None, None, None, None),

        # Owners, editors, and admins cannot assign metadata from other workspaces to datastreams
        ("owner", "27c70b41-e845-40ea-8cc7-d1b40f89816b", "76dadda5-224b-4e1f-8570-e385bd482b2d", None, None, None,
         None, "You cannot associate this datastream with a thing in another workspace", 400),
        ("owner", "27c70b41-e845-40ea-8cc7-d1b40f89816b", None, "5dbfd184-ae79-4c05-a9ea-3f5e775ecbc1", None, None,
         None, "The given observed property cannot be associated", 400),
        ("owner", "27c70b41-e845-40ea-8cc7-d1b40f89816b", None, None, "fa3c97ce-41b8-4c12-b91a-9127ce0c083a", None,
         None, "The given processing level cannot be associated", 400),
        ("owner", "27c70b41-e845-40ea-8cc7-d1b40f89816b", None, None, None, "89a6ae16-9f85-4279-985e-83484db47107",
         None, "The given sensor cannot be associated", 400),
        ("owner", "27c70b41-e845-40ea-8cc7-d1b40f89816b", None, None, None, None,
         "98a74429-2be2-44c0-8f7f-2df2ca12893d", "The given unit cannot be associated", 400),
        ("admin", "27c70b41-e845-40ea-8cc7-d1b40f89816b", "76dadda5-224b-4e1f-8570-e385bd482b2d", None, None, None,
         None, "You cannot associate this datastream with a thing in another workspace", 400),
        ("admin", "27c70b41-e845-40ea-8cc7-d1b40f89816b", None, "5dbfd184-ae79-4c05-a9ea-3f5e775ecbc1", None, None,
         None, "The given observed property cannot be associated", 400),
        ("admin", "27c70b41-e845-40ea-8cc7-d1b40f89816b", None, None, "fa3c97ce-41b8-4c12-b91a-9127ce0c083a", None,
         None, "The given processing level cannot be associated", 400),
        ("admin", "27c70b41-e845-40ea-8cc7-d1b40f89816b", None, None, None, "89a6ae16-9f85-4279-985e-83484db47107",
         None, "The given sensor cannot be associated", 400),
        ("admin", "27c70b41-e845-40ea-8cc7-d1b40f89816b", None, None, None, None,
         "98a74429-2be2-44c0-8f7f-2df2ca12893d", "The given unit cannot be associated", 400),
        ("editor", "27c70b41-e845-40ea-8cc7-d1b40f89816b", "76dadda5-224b-4e1f-8570-e385bd482b2d", None, None, None,
         None, "You cannot associate this datastream with a thing in another workspace", 400),
        ("editor", "27c70b41-e845-40ea-8cc7-d1b40f89816b", None, "5dbfd184-ae79-4c05-a9ea-3f5e775ecbc1", None, None,
         None, "The given observed property cannot be associated", 400),
        ("editor", "27c70b41-e845-40ea-8cc7-d1b40f89816b", None, None, "fa3c97ce-41b8-4c12-b91a-9127ce0c083a", None,
         None, "The given processing level cannot be associated", 400),
        ("editor", "27c70b41-e845-40ea-8cc7-d1b40f89816b", None, None, None, "89a6ae16-9f85-4279-985e-83484db47107",
         None, "The given sensor cannot be associated", 400),
        ("editor", "27c70b41-e845-40ea-8cc7-d1b40f89816b", None, None, None, None,
         "98a74429-2be2-44c0-8f7f-2df2ca12893d", "The given unit cannot be associated", 400),

        # Owners, editors, and admins cannot assign non-existent metadata to datastreams
        ("owner", "27c70b41-e845-40ea-8cc7-d1b40f89816b", "00000000-0000-0000-0000-000000000000", None, None, None,
         None, "Thing does not exist", 400),
        ("owner", "27c70b41-e845-40ea-8cc7-d1b40f89816b", None, "00000000-0000-0000-0000-000000000000", None, None,
         None, "Observed property does not exist", 400),
        ("owner", "27c70b41-e845-40ea-8cc7-d1b40f89816b", None, None, "00000000-0000-0000-0000-000000000000", None,
         None, "Processing level does not exist", 400),
        ("owner", "27c70b41-e845-40ea-8cc7-d1b40f89816b", None, None, None, "00000000-0000-0000-0000-000000000000",
         None, "Sensor does not exist", 400),
        ("owner", "27c70b41-e845-40ea-8cc7-d1b40f89816b", None, None, None, None,
         "00000000-0000-0000-0000-000000000000", "Unit does not exist", 400),
        ("admin", "27c70b41-e845-40ea-8cc7-d1b40f89816b", "00000000-0000-0000-0000-000000000000", None, None, None,
         None, "Thing does not exist", 400),
        ("admin", "27c70b41-e845-40ea-8cc7-d1b40f89816b", None, "00000000-0000-0000-0000-000000000000", None, None,
         None, "Observed property does not exist", 400),
        ("admin", "27c70b41-e845-40ea-8cc7-d1b40f89816b", None, None, "00000000-0000-0000-0000-000000000000", None,
         None, "Processing level does not exist", 400),
        ("admin", "27c70b41-e845-40ea-8cc7-d1b40f89816b", None, None, None, "00000000-0000-0000-0000-000000000000",
         None, "Sensor does not exist", 400),
        ("admin", "27c70b41-e845-40ea-8cc7-d1b40f89816b", None, None, None, None,
         "00000000-0000-0000-0000-000000000000", "Unit does not exist", 400),
        ("editor", "27c70b41-e845-40ea-8cc7-d1b40f89816b", "00000000-0000-0000-0000-000000000000", None, None, None,
         None, "Thing does not exist", 400),
        ("editor", "27c70b41-e845-40ea-8cc7-d1b40f89816b", None, "00000000-0000-0000-0000-000000000000", None, None,
         None, "Observed property does not exist", 400),
        ("editor", "27c70b41-e845-40ea-8cc7-d1b40f89816b", None, None, "00000000-0000-0000-0000-000000000000", None,
         None, "Processing level does not exist", 400),
        ("editor", "27c70b41-e845-40ea-8cc7-d1b40f89816b", None, None, None, "00000000-0000-0000-0000-000000000000",
         None, "Sensor does not exist", 400),
        ("editor", "27c70b41-e845-40ea-8cc7-d1b40f89816b", None, None, None, None,
         "00000000-0000-0000-0000-000000000000", "Unit does not exist", 400),

        # Viewers and anonymous cannot edit datastreams
        ("viewer", "27c70b41-e845-40ea-8cc7-d1b40f89816b", None, None, None, None, None, "You do not have permission",
         403),
        ("viewer", "9f96957b-ee20-4c7b-bf2b-673a0cda3a04", None, None, None, None, None, "You do not have permission",
         403),
        ("anonymous", "27c70b41-e845-40ea-8cc7-d1b40f89816b", None, None, None, None, None,
         "You do not have permission", 403),
        ("anonymous", "e0506cac-3e50-4d0a-814d-7ae0146705b2", None, None, None, None, None, "Datastream does not exist",
         404),
        ("anonymous", "cad40a75-99ca-4317-b534-0fc7880c905f", None, None, None, None, None, "Datastream does not exist",
         404),
        ("anonymous", "fcd47d93-4cae-411a-9e1e-26ef473840ed", None, None, None, None, None, "Datastream does not exist",
         404),
        ("anonymous", "dd1f9293-ce29-4b6a-88e6-d65110d1be65", None, None, None, None, None, "Datastream does not exist",
         404),
        ("anonymous", "1c9a797e-6fd8-4e99-b1ae-87ab4affc0a2", None, None, None, None, None, "Datastream does not exist",
         404),
        ("anonymous", "42e08eea-27bb-4ea3-8ced-63acff0f3334", None, None, None, None, None, "Datastream does not exist",
         404),
        ("anonymous", "9f96957b-ee20-4c7b-bf2b-673a0cda3a04", None, None, None, None, None, "Datastream does not exist",
         404),
        ("anonymous", "00000000-0000-0000-0000-000000000000", None, None, None, None, None, "Datastream does not exist",
         404),
    ]
)
def test_edit_datastream(get_user, user, datastream, thing, observed_property, processing_level, sensor, unit, message,
                         error_code):
    datastream_dict = {}
    if thing:
        datastream_dict["thing_id"] = uuid.UUID(thing)
    if observed_property:
        datastream_dict["observed_property_id"] = uuid.UUID(observed_property)
    if processing_level:
        datastream_dict["processing_level_id"] = uuid.UUID(processing_level)
    if sensor:
        datastream_dict["sensor_id"] = uuid.UUID(sensor)
    if unit:
        datastream_dict["unit_id"] = uuid.UUID(unit)
    datastream_data = DatastreamPatchBody(**datastream_dict)
    if error_code:
        with pytest.raises(HttpError) as exc_info:
            datastream_service.update(
                user=get_user(user), uid=uuid.UUID(datastream), data=datastream_data
            )
        assert exc_info.value.status_code == error_code
        assert exc_info.value.message.startswith(message)
    else:
        datastream_update = datastream_service.update(
            user=get_user(user), uid=uuid.UUID(datastream), data=datastream_data
        )
        if thing:
            assert datastream_update.thing_id == datastream_data.thing_id
        if observed_property:
            assert datastream_update.observed_property_id == datastream_data.observed_property_id
        if processing_level:
            assert datastream_update.processing_level_id == datastream_data.processing_level_id
        if sensor:
            assert datastream_update.sensor_id == datastream_data.sensor_id
        if unit:
            assert datastream_update.unit_id == datastream_data.unit_id


@pytest.mark.parametrize("user, datastream, message, error_code, max_queries", [
    # Owners, admins, editors can delete public and private datastreams
    ("owner", "27c70b41-e845-40ea-8cc7-d1b40f89816b", "Public Datastream 1", None, 6),
    ("owner", "9f96957b-ee20-4c7b-bf2b-673a0cda3a04", "Private Datastream 7", None, 6),
    ("admin", "27c70b41-e845-40ea-8cc7-d1b40f89816b", "Public Datastream 1", None, 6),
    ("admin", "9f96957b-ee20-4c7b-bf2b-673a0cda3a04", "Private Datastream 7", None, 6),
    ("editor", "27c70b41-e845-40ea-8cc7-d1b40f89816b", "Public Datastream 1", None, 6),
    ("editor", "9f96957b-ee20-4c7b-bf2b-673a0cda3a04", "Private Datastream 7", None, 6),

    # Anonymous and viewers cannot delete datastreams
    ("viewer", "27c70b41-e845-40ea-8cc7-d1b40f89816b", "You do not have permission", 403, 4),
    ("viewer", "9f96957b-ee20-4c7b-bf2b-673a0cda3a04", "You do not have permission", 403, 4),
    ("anonymous", "27c70b41-e845-40ea-8cc7-d1b40f89816b", "You do not have permission", 403, 4),
    ("anonymous", "e0506cac-3e50-4d0a-814d-7ae0146705b2", "Datastream does not exist", 404, 4),
    ("anonymous", "cad40a75-99ca-4317-b534-0fc7880c905f", "Datastream does not exist", 404, 4),
    ("anonymous", "fcd47d93-4cae-411a-9e1e-26ef473840ed", "Datastream does not exist", 404, 4),
    ("anonymous", "dd1f9293-ce29-4b6a-88e6-d65110d1be65", "Datastream does not exist", 404, 4),
    ("anonymous", "1c9a797e-6fd8-4e99-b1ae-87ab4affc0a2", "Datastream does not exist", 404, 4),
    ("anonymous", "42e08eea-27bb-4ea3-8ced-63acff0f3334", "Datastream does not exist", 404, 4),
    ("anonymous", "9f96957b-ee20-4c7b-bf2b-673a0cda3a04", "Datastream does not exist", 404, 4),
    ("anonymous", "00000000-0000-0000-0000-000000000000", "Datastream does not exist", 404, 4),
])
def test_delete_datastream(django_assert_max_num_queries, get_user, user, datastream, message, error_code, max_queries):
    with django_assert_max_num_queries(max_queries):
        if error_code:
            with pytest.raises(HttpError) as exc_info:
                datastream_service.delete(
                    user=get_user(user), uid=uuid.UUID(datastream)
                )
            assert exc_info.value.status_code == error_code
            assert exc_info.value.message.startswith(message)
        else:
            datastream_delete = datastream_service.delete(
                user=get_user(user), uid=uuid.UUID(datastream)
            )
            assert datastream_delete == "Datastream deleted"
