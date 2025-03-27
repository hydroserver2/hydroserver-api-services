import uuid
from ninja import Router, Path
from typing import Optional
from django.db import transaction
from hydroserver.security import bearer_auth, session_auth, anonymous_auth
from hydroserver.http import HydroServerHttpRequest
from sta.schemas import SensorGetResponse, SensorPostBody, SensorPatchBody
from sta.services import SensorService

sensor_router = Router(tags=["Sensors"])
sensor_service = SensorService()


@sensor_router.get(
    "",
    auth=[session_auth, bearer_auth, anonymous_auth],
    response={
        200: list[SensorGetResponse],
        401: str,
    },
    by_alias=True,
)
def get_sensors(
    request: HydroServerHttpRequest, workspace_id: Optional[uuid.UUID] = None
):
    """
    Get public Sensors and Sensors associated with the authenticated user.
    """

    return 200, sensor_service.list(
        user=request.authenticated_user, workspace_id=workspace_id
    )


@sensor_router.post(
    "",
    auth=[session_auth, bearer_auth],
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

    return 201, sensor_service.create(user=request.authenticated_user, data=data)


@sensor_router.get(
    "/{sensor_id}",
    auth=[session_auth, bearer_auth, anonymous_auth],
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

    return 200, sensor_service.get(user=request.authenticated_user, uid=sensor_id)


@sensor_router.patch(
    "/{sensor_id}",
    auth=[session_auth, bearer_auth],
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
        user=request.authenticated_user, uid=sensor_id, data=data
    )


@sensor_router.delete(
    "/{sensor_id}",
    auth=[session_auth, bearer_auth],
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

    return 204, sensor_service.delete(user=request.authenticated_user, uid=sensor_id)
