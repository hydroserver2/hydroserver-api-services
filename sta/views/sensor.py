import uuid
from ninja import Router, Path, Query
from django.http import HttpResponse
from django.db import transaction
from hydroserver.security import bearer_auth, session_auth, apikey_auth, anonymous_auth
from hydroserver.http import HydroServerHttpRequest
from sta.schemas import (
    SensorGetResponse,
    SensorQueryParameters,
    SensorPostBody,
    SensorPatchBody,
)
from sta.services import SensorService

sensor_router = Router(tags=["Sensors"])
sensor_service = SensorService()


@sensor_router.get(
    "",
    auth=[session_auth, bearer_auth, apikey_auth, anonymous_auth],
    response={
        200: list[SensorGetResponse],
        401: str,
    },
    by_alias=True,
)
def get_sensors(
    request: HydroServerHttpRequest,
    response: HttpResponse,
    query: Query[SensorQueryParameters],
):
    """
    Get public Sensors and Sensors associated with the authenticated user.
    """

    return 200, sensor_service.list(
        principal=request.principal,
        response=response,
        page=query.page,
        page_size=query.page_size,
        ordering=query.ordering,
        filtering=query.dict(exclude_unset=True),
    )


@sensor_router.post(
    "",
    auth=[session_auth, bearer_auth, apikey_auth],
    response={
        201: SensorGetResponse,
        400: str,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True,
)
@transaction.atomic
def create_sensor(request: HydroServerHttpRequest, data: SensorPostBody):
    """
    Create a new Sensor.
    """

    return 201, sensor_service.create(principal=request.principal, data=data)


@sensor_router.get(
    "/{sensor_id}",
    auth=[session_auth, bearer_auth, apikey_auth, anonymous_auth],
    response={
        200: SensorGetResponse,
        401: str,
        403: str,
    },
    by_alias=True,
    exclude_unset=True,
)
def get_sensor(request: HydroServerHttpRequest, sensor_id: Path[uuid.UUID]):
    """
    Get a Sensor.
    """

    return 200, sensor_service.get(principal=request.principal, uid=sensor_id)


@sensor_router.patch(
    "/{sensor_id}",
    auth=[session_auth, bearer_auth, apikey_auth],
    response={
        200: SensorGetResponse,
        400: str,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True,
)
@transaction.atomic
def update_sensor(
    request: HydroServerHttpRequest, sensor_id: Path[uuid.UUID], data: SensorPatchBody
):
    """
    Update a Sensor.
    """

    return 200, sensor_service.update(
        principal=request.principal, uid=sensor_id, data=data
    )


@sensor_router.delete(
    "/{sensor_id}",
    auth=[session_auth, bearer_auth, apikey_auth],
    response={
        204: str,
        401: str,
        403: str,
        409: str,
    },
    by_alias=True,
)
@transaction.atomic
def delete_sensor(request: HydroServerHttpRequest, sensor_id: Path[uuid.UUID]):
    """
    Delete a Sensor.
    """

    return 204, sensor_service.delete(principal=request.principal, uid=sensor_id)
