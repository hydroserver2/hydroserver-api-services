from ninja import Router, Query
# from ninja.security import django_auth
from django.http import HttpResponse
from sensorthings.api.core.schemas import Filters
from sensorthings.api.core.main import SensorThingsRequest
from .schemas import HistoricalLocationPostBody, HistoricalLocationPatchBody, HistoricalLocationListResponse, \
    HistoricalLocationGetResponse


router = Router(tags=['Historical Locations'])


@router.get(
    '/HistoricalLocations',
    # auth=django_auth,
    # response={200, HistoricalLocationListResponse},
    by_alias=True,
    url_name='list_historical_location'
)
def get_historical_locations(request: SensorThingsRequest, filters: Filters = Query(...)):
    """"""

    return {}


@router.get(
    '/HistoricalLocations({historical_location_id})',
    # auth=django_auth,
    # response={200, HistoricalLocationGetResponse},
    by_alias=True
)
def get_historical_location(request: SensorThingsRequest, historical_location_id: str):
    """"""

    return {}


@router.post(
    '/HistoricalLocations',
    # auth=django_auth,
    response={201: None}
)
def create_historical_location(
        request: SensorThingsRequest,
        response: HttpResponse,
        historical_location: HistoricalLocationPostBody
):
    """
    Create a new Historical Location entity.

    Links:
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/historical-location/properties" target="_blank">\
      Historical Location Properties</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/historical-location/relations" target="_blank">\
      Historical Location Relations</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/create-entity" target="_blank">\
      Create Entity</a>
    """

    historical_location_id = request.engine.create(
        entity_body=historical_location
    )

    response['location'] = request.engine.get_ref(
        entity_id=historical_location_id
    )

    return 201, None


@router.patch(
    '/HistoricalLocations({historical_location_id})',
    # auth=django_auth,
    response={204: None}
)
def update_historical_location(
        request: SensorThingsRequest,
        historical_location_id: str,
        historical_location: HistoricalLocationPatchBody
):
    """
    Update an existing Historical Location entity.

    Links:
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/historical-location/properties" target="_blank">\
      Historical Location Properties</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/historical-location/relations" target="_blank">\
      Historical Location Relations</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/update-entity" target="_blank">\
      Update Entity</a>
    """

    request.engine.update(
        entity_id=historical_location_id,
        entity_body=historical_location
    )

    return 204, None


@router.delete(
    '/HistoricalLocations({historical_location_id})',
    # auth=django_auth,
    response={204: None}
)
def delete_historical_location(request: SensorThingsRequest, historical_location_id: str):
    """
    Delete a Historical Location entity.

    Links:
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/delete-entity" target="_blank">\
      Delete Entity</a>
    """

    request.engine.delete(
        entity_id=historical_location_id
    )

    return 204, None
