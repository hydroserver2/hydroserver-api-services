from ninja import Router, Query
from ninja.security import django_auth
from django.http import HttpResponse
from sensorthings.api.core.schemas import Filters
from sensorthings.api.core.main import SensorThingsRequest
from .schemas import DatastreamPostBody, DatastreamPatchBody, DatastreamListResponse, DatastreamGetResponse


router = Router(tags=['Datastreams'])


@router.get(
    '/Datastreams',
    # auth=django_auth,
    # response={200, DatastreamListResponse},
    by_alias=True,
    url_name='list_datastream'
)
def get_datastreams(request: SensorThingsRequest, filters: Filters = Query(...)):
    """"""

    return {}


@router.get(
    '/Datastreams({datastream_id})',
    # auth=django_auth,
    # response={200, DatastreamGetResponse},
    by_alias=True
)
def get_datastream(request: SensorThingsRequest, datastream_id: str):
    """"""

    return {}


@router.post(
    '/Datastreams',
    # auth=django_auth,
    response={201: None}
)
def create_datastream(request: SensorThingsRequest, response: HttpResponse, datastream: DatastreamPostBody):
    """
    Create a new Datastream entity.

    Links:
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/datastream/properties" target="_blank">\
      Datastream Properties</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/datastream/relations" target="_blank">\
      Datastream Relations</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/create-entity" target="_blank">\
      Create Entity</a>
    """

    datastream_id = request.engine.create(
        entity_body=datastream
    )

    response['location'] = request.engine.get_ref(
        entity_id=datastream_id
    )

    return 201, None


@router.patch(
    '/Datastreams({datastream_id})',
    # auth=django_auth,
    response={204: None}
)
def update_datastream(request: SensorThingsRequest, datastream_id: str, datastream: DatastreamPatchBody):
    """
    Update an existing Datastream entity.

    Links:
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/datastream/properties" target="_blank">\
      Datastream Properties</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/datastream/relations" target="_blank">\
      Datastream Relations</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/update-entity" target="_blank">\
      Update Entity</a>
    """

    request.engine.update(
        entity_id=datastream_id,
        entity_body=datastream
    )

    return 204, None


@router.delete(
    '/Datastreams({datastream_id})',
    # auth=django_auth,
    response={204: None}
)
def delete_datastream(request: SensorThingsRequest, datastream_id: str):
    """
    Delete a Datastream entity.

    Links:
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/delete-entity" target="_blank">\
      Delete Entity</a>
    """

    request.engine.delete(
        entity_id=datastream_id
    )

    return 204, None
