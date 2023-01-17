from ninja import Router, Query
from ninja.security import django_auth
from django.http import HttpResponse
from sensorthings.api.core.schemas import Filters
from sensorthings.api.core.main import SensorThingsRequest
from .schemas import LocationPostBody, LocationPatchBody, LocationListResponse, LocationGetResponse


router = Router(tags=['Locations'])


@router.get(
    '/Locations',
    # auth=django_auth,
    # response={200, LocationListResponse},
    by_alias=True,
    url_name='list_location'
)
def get_locations(request: SensorThingsRequest, filters: Filters = Query(...)):
    """"""

    return {}


@router.get(
    '/Locations({location_id})',
    # auth=django_auth,
    # response={200, LocationGetResponse},
    by_alias=True
)
def get_location(request: SensorThingsRequest, location_id: str):
    """"""

    return {}


@router.post(
    '/Locations',
    # auth=django_auth,
    response={201: None}
)
def create_location(request: SensorThingsRequest, response: HttpResponse, location: LocationPostBody):
    """
    Create a new Location entity.

    Links:
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/location/properties" target="_blank">\
      Location Properties</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/location/relations" target="_blank">\
      Location Relations</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/create-entity" target="_blank">\
      Create Entity</a>
    """

    location_id = request.engine.create(
        entity_body=location
    )

    response['location'] = request.engine.get_ref(
        entity_id=location_id
    )

    return 201, None


@router.patch(
    '/Locations({location_id})',
    # auth=django_auth,
    response={204: None}
)
def update_location(request: SensorThingsRequest, location_id: str, location: LocationPatchBody):
    """
    Update an existing Location entity.

    Links:
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/location/properties" target="_blank">\
      Location Properties</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/location/relations" target="_blank">\
      Location Relations</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/update-entity" target="_blank">\
      Update Entity</a>
    """

    request.engine.update(
        entity_id=location_id,
        entity_body=location
    )

    return 204, None


@router.delete(
    '/Locations({location_id})',
    # auth=django_auth,
    response={204: None}
)
def delete_location(request: SensorThingsRequest, location_id: str):
    """
    Delete a Location entity.

    Links:
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/delete-entity" target="_blank">\
      Delete Entity</a>
    """

    request.engine.delete(
        entity_id=location_id
    )

    return 204, None
