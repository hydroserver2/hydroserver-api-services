from ninja import Router, Query
from ninja.security import django_auth
from django.http import HttpResponse
from sensorthings.api.core.schemas import Filters
from sensorthings.api.core.main import SensorThingsRequest
from .schemas import ObservationPostBody, ObservationPatchBody, ObservationListResponse, ObservationGetResponse


router = Router(tags=['Observations'])


@router.get(
    '/Observations',
    # auth=django_auth,
    # response={200, ObservationListResponse},
    by_alias=True,
    url_name='list_observation'
)
def get_observations(request: SensorThingsRequest, filters: Filters = Query(...)):
    """"""

    return {}


@router.get(
    '/Observations({observation_id})',
    # auth=django_auth,
    # response={200, ObservationGetResponse},
    by_alias=True
)
def get_observation(request: SensorThingsRequest, observation_id: str):
    """"""

    return {}


@router.post(
    '/Observations',
    # auth=django_auth,
    response={201: None}
)
def create_observation(request: SensorThingsRequest, response: HttpResponse, observation: ObservationPostBody):
    """
    Create a new Observation entity.

    Links:
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/observation/properties" target="_blank">\
      Observation Properties</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/observation/relations" target="_blank">\
      Observation Relations</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/create-entity" target="_blank">\
      Create Entity</a>
    """

    observation_id = request.engine.create(
        entity_body=observation
    )

    response['location'] = request.engine.get_ref(
        entity_id=observation_id
    )

    return 201, None


@router.patch(
    '/Observations({observation_id})',
    # auth=django_auth,
    response={204: None}
)
def update_observation(request: SensorThingsRequest, observation_id: str, observation: ObservationPatchBody):
    """
    Update an existing Observation entity.

    Links:
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/observation/properties" target="_blank">\
      Observation Properties</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/datamodel/observation/relations" target="_blank">\
      Observation Relations</a> -
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/update-entity" target="_blank">\
      Update Entity</a>
    """

    request.engine.update(
        entity_id=observation_id,
        entity_body=observation
    )

    return 204, None


@router.delete(
    '/Observations({observation_id})',
    # auth=django_auth,
    response={204: None}
)
def delete_observation(request: SensorThingsRequest, observation_id: str):
    """
    Delete a Observation entity.

    Links:
    <a href="http://www.opengis.net/spec/iot_sensing/1.1/req/create-update-delete/delete-entity" target="_blank">\
      Delete Entity</a>
    """

    request.engine.delete(
        entity_id=observation_id
    )

    return 204, None