from ninja import Router, Query
from ninja.security import django_auth
from django.http import HttpResponse
from sensorthings.api.core.schemas import Filters
from sensorthings.api.core.main import SensorThingsRequest
from .schemas import ThingPostBody, ThingPatchBody, ThingListResponse, ThingGetResponse


router = Router(tags=['Things'])


@router.get(
    '/Things',
    # auth=django_auth,
    # response={200, ThingListResponse},
    by_alias=True,
    url_name='list_thing'
)
def get_things(request: SensorThingsRequest, filters: Filters = Query(...)):
    """"""

    return {}


@router.get(
    '/Things({thing_id})',
    # auth=django_auth,
    # response={200, ThingGetResponse},
    by_alias=True
)
def get_thing(request: SensorThingsRequest, thing_id: str):
    """"""

    return {}


@router.post(
    '/Things',
    # auth=django_auth,
    response={201: None}
)
def create_thing(request: SensorThingsRequest, response: HttpResponse, thing: ThingPostBody):
    """
    Create a new Thing entity.

    Links:
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/thing/properties" target="_blank">\
      Thing Properties</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/thing/relations" target="_blank">\
      Thing Relations</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/create-entity" target="_blank">\
      Create Entity</a>
    """

    thing_id = request.engine.create(
        entity_body=thing
    )

    response['location'] = request.engine.get_ref(
        entity_id=thing_id
    )

    return 201, None


@router.patch(
    '/Things({thing_id})',
    # auth=django_auth,
    response={204: None}
)
def update_thing(request: SensorThingsRequest, thing_id: str, thing: ThingPatchBody):
    """
    Update an existing Thing entity.

    Links:
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/thing/properties" target="_blank">\
      Thing Properties</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/thing/relations" target="_blank">\
      Thing Relations</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/update-entity" target="_blank">\
      Update Entity</a>
    """

    request.engine.update(
        entity_id=thing_id,
        entity_body=thing
    )

    return 204, None


@router.delete(
    '/Things({thing_id})',
    # auth=django_auth,
    response={204: None}
)
def delete_thing(request: SensorThingsRequest, thing_id: str):
    """
    Delete a Thing entity.

    Links:
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/delete-entity" target="_blank">\
      Delete Entity</a>
    """

    request.engine.delete(
        entity_id=thing_id
    )

    return 204, None
