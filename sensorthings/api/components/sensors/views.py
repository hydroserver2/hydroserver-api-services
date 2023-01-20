from ninja import Router, Query
from ninja.security import django_auth
from django.http import HttpResponse
from sensorthings.api.core.schemas import Filters
from sensorthings.api.core.main import SensorThingsRequest
from .schemas import SensorPostBody, SensorPatchBody, SensorListResponse, SensorGetResponse


router = Router(tags=['Sensors'])


@router.get(
    '/Sensors',
    # auth=django_auth,
    # response={200, SensorListResponse},
    by_alias=True,
    url_name='list_sensor'
)
def get_sensors(request, filters: Filters = Query(...)):
    """"""

    return {}


@router.get(
    '/Sensors({sensor_id})',
    # auth=django_auth,
    # response={200, SensorGetResponse},
)
def get_sensor(request, sensor_id: str):
    """"""

    return {}


@router.post(
    '/Sensors',
    # auth=django_auth,
    response={201: None}
)
def create_sensor(request: SensorThingsRequest, response: HttpResponse, sensor: SensorPostBody):
    """
    Create a new Sensor entity.

    Links:
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/sensor/properties" target="_blank">\
      Sensor Properties</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/sensor/relations" target="_blank">\
      Sensor Relations</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/create-entity" target="_blank">\
      Create Entity</a>
    """

    sensor_id = request.engine.create(
        entity_body=sensor
    )

    response['location'] = request.engine.get_ref(
        entity_id=sensor_id
    )

    return 201, None


@router.patch(
    '/Sensors({sensor_id})',
    # auth=django_auth,
    response={204: None}
)
def update_sensor(request: SensorThingsRequest, sensor_id: str, sensor: SensorPatchBody):
    """
    Update an existing Sensor entity.

    Links:
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/sensor/properties" target="_blank">\
      Sensor Properties</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/sensor/relations" target="_blank">\
      Sensor Relations</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/update-entity" target="_blank">\
      Update Entity</a>
    """

    request.engine.update(
        entity_id=sensor_id,
        entity_body=sensor
    )

    return 204, None


@router.delete(
    '/Sensors({sensor_id})',
    # auth=django_auth,
    response={204: None}
)
def delete_sensor(request, sensor_id: str):
    """
    Delete a Sensor entity.

    Links:
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/delete-entity" target="_blank">\
      Delete Entity</a>
    """

    request.engine.delete(
        entity_id=sensor_id
    )

    return 204, None
