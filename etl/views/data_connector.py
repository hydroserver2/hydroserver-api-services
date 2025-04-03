import uuid
from ninja import Router, Path
from typing import Optional
from django.db import transaction
from hydroserver.security import bearer_auth, session_auth
from hydroserver.http import HydroServerHttpRequest
from etl.schemas import (
    DataConnectorGetResponse,
    DataConnectorPostBody,
    DataConnectorPatchBody,
    LinkedDatastreamGetResponse,
    LinkedDatastreamPostBody,
    LinkedDatastreamPatchBody
)
from etl.services import DataConnectorService

data_connector_router = Router(tags=["Data Connectors"])
data_connector_service = DataConnectorService()


@data_connector_router.get(
    "",
    auth=[session_auth, bearer_auth],
    response={
        200: list[DataConnectorGetResponse],
        401: str,
    },
    by_alias=True,
)
def get_data_connectors(
    request: HydroServerHttpRequest,
    workspace_id: Optional[uuid.UUID] = None,
    etl_system_platform_id: Optional[uuid.UUID] = None,
    etl_system_id: Optional[uuid.UUID] = None,
):
    """
    Get public Data Connectors and Data Connectors associated with the authenticated user.
    """

    return 200, data_connector_service.list(
        user=request.authenticated_user,
        workspace_id=workspace_id,
        etl_system_platform_id=etl_system_platform_id,
        etl_system_id=etl_system_id,
    )


@data_connector_router.post(
    "",
    auth=[session_auth, bearer_auth],
    response={
        201: DataConnectorGetResponse,
        400: str,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True,
)
@transaction.atomic
def create_data_connector(request: HydroServerHttpRequest, data: DataConnectorPostBody):
    """
    Create a new Data Connector.
    """

    return 201, data_connector_service.create(user=request.authenticated_user, data=data)


@data_connector_router.get(
    "/{data_connector_id}",
    auth=[session_auth, bearer_auth],
    response={
        200: DataConnectorGetResponse,
        401: str,
        403: str,
    },
    by_alias=True,
    exclude_unset=True,
)
def get_data_connector(request: HydroServerHttpRequest, data_connector_id: Path[uuid.UUID]):
    """
    Get a Data Connector.
    """

    return 200, data_connector_service.get(
        user=request.authenticated_user, uid=data_connector_id
    )


@data_connector_router.patch(
    "/{data_connector_id}",
    auth=[session_auth, bearer_auth],
    response={
        200: DataConnectorGetResponse,
        400: str,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True,
)
@transaction.atomic
def update_data_connector(
    request: HydroServerHttpRequest,
    data_connector_id: Path[uuid.UUID],
    data: DataConnectorPatchBody,
):
    """
    Update a Data Connector.
    """

    return 200, data_connector_service.update(
        user=request.authenticated_user, uid=data_connector_id, data=data
    )


@data_connector_router.delete(
    "/{data_connector_id}",
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
def delete_data_connector(
    request: HydroServerHttpRequest, data_connector_id: Path[uuid.UUID]
):
    """
    Delete a Data Connector.
    """

    return 204, data_connector_service.delete(
        user=request.authenticated_user, uid=data_connector_id
    )


@data_connector_router.get(
    "/{data_connector_id}/datastreams",
    auth=[session_auth, bearer_auth],
    response={
        200: list[LinkedDatastreamGetResponse],
        401: str,
    },
    by_alias=True,
)
def get_linked_datastreams(
    request: HydroServerHttpRequest, data_connector_id: Path[uuid.UUID]
):
    """
    Get public Datastreams and Datastreams associated with the authenticated user linked to a Data Connector.
    """

    return 200, data_connector_service.list_linked_datastreams(
        user=request.authenticated_user, uid=data_connector_id
    )


@data_connector_router.post(
    "/{data_connector_id}/datastreams/{datastream_id}",
    auth=[session_auth, bearer_auth],
    response={
        201: LinkedDatastreamGetResponse,
        400: str,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True,
)
@transaction.atomic
def link_datastream(
    request: HydroServerHttpRequest,
    data_connector_id: Path[uuid.UUID],
    datastream_id: Path[uuid.UUID],
    data: LinkedDatastreamPostBody,
):
    """
    Link a Datastream to a Data Connector.
    """

    return 201, data_connector_service.link_datastream(
        user=request.authenticated_user,
        uid=data_connector_id,
        datastream_id=datastream_id,
        data=data,
    )


@data_connector_router.get(
    "/{data_connector_id}/datastreams/{datastream_id}",
    auth=[session_auth, bearer_auth],
    response={
        200: LinkedDatastreamGetResponse,
        401: str,
        403: str,
    },
    by_alias=True,
    exclude_unset=True,
)
def get_linked_datastream(
    request: HydroServerHttpRequest,
    data_connector_id: Path[uuid.UUID],
    datastream_id: Path[uuid.UUID],
):
    """
    Get a Datastream linked to a Data Connector.
    """

    return 200, data_connector_service.get_linked_datastream(
        user=request.authenticated_user, uid=data_connector_id, datastream_id=datastream_id
    )


@data_connector_router.patch(
    "/{data_connector_id}/datastreams/{datastream_id}",
    auth=[session_auth, bearer_auth],
    response={
        200: LinkedDatastreamGetResponse,
        400: str,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True,
)
@transaction.atomic
def update_linked_datastream(
    request: HydroServerHttpRequest,
    data_connector_id: Path[uuid.UUID],
    datastream_id: Path[uuid.UUID],
    data: LinkedDatastreamPatchBody,
):
    """
    Update a linked Datastream.
    """

    return 200, data_connector_service.update_linked_datastream(
        user=request.authenticated_user,
        uid=data_connector_id,
        datastream_id=datastream_id,
        data=data,
    )


@data_connector_router.delete(
    "/{data_connector_id}/datastreams/{datastream_id}",
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
def unlink_datastream(
    request: HydroServerHttpRequest,
    data_connector_id: Path[uuid.UUID],
    datastream_id: Path[uuid.UUID],
):
    """
    Unlink a Datastream from a Data Connector.
    """

    return 204, data_connector_service.unlink_datastream(
        user=request.authenticated_user, uid=data_connector_id, datastream_id=datastream_id
    )
