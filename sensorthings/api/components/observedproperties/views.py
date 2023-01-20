from ninja import Router, Query
from ninja.security import django_auth
from django.http import HttpResponse
from sensorthings.api.core.schemas import Filters
from sensorthings.api.core.main import SensorThingsRequest
from .schemas import ObservedPropertyPostBody, ObservedPropertyPatchBody, ObservedPropertyListResponse, \
    ObservedPropertyGetResponse


router = Router(tags=['Observed Properties'])


@router.get(
    '/ObservedProperties',
    # auth=django_auth,
    # response={200, ObservedPropertyListResponse},
    url_name='list_observed_property'
)
def get_observed_properties(request: SensorThingsRequest, filters: Filters = Query(...)):
    """"""

    return {}


@router.get(
    '/ObservedProperties({observed_property_id})',
    # auth=django_auth,
    # response={200, ThingGetResponse},
    by_alias=True
)
def get_observed_property(request, observed_property_id: str):
    """"""

    return {}


@router.post(
    '/ObservedProperties',
    # auth=django_auth,
    response={201: None}
)
def create_observed_property(
        request: SensorThingsRequest,
        response: HttpResponse,
        observed_property: ObservedPropertyPostBody
):
    """
    Create a new Observed Property entity.

    Links:
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/observed-property/properties" target="_blank">\
      Observed Property Properties</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/observed-property/relations" target="_blank">\
      Observed Property Relations</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/create-entity" target="_blank">\
      Create Entity</a>
    """

    observed_property_id = request.engine.create(
        entity_body=observed_property
    )

    response['location'] = request.engine.get_ref(
        entity_id=observed_property_id
    )

    return 201, None


@router.patch(
    '/ObservedProperties({observed_property_id})',
    # auth=django_auth,
    response={204: None}
)
def update_observed_property(
        request: SensorThingsRequest,
        observed_property_id: str,
        observed_property: ObservedPropertyPatchBody
):
    """
    Update an existing Observed Property entity.

    Links:
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/observed-property/properties" target="_blank">\
      Thing Properties</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/observed-property/relations" target="_blank">\
      Thing Relations</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/update-entity" target="_blank">\
      Update Entity</a>
    """

    request.engine.update(
        entity_id=observed_property_id,
        entity_body=observed_property
    )

    return 204, None


@router.delete(
    '/ObservedProperties({observed_property_id})',
    # auth=django_auth,
    response={204: None}
)
def delete_observed_property(request: SensorThingsRequest, observed_property_id: str):
    """
    Delete an Observed Property entity.

    Links:
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/delete-entity" target="_blank">\
      Delete Entity</a>
    """

    request.engine.delete(
        entity_id=observed_property_id
    )

    return 204, None
