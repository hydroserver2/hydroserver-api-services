import uuid
from ninja import Router, Path
from typing import Optional
from django.db import transaction
from hydroserver.security import bearer_auth, session_auth, apikey_auth
from hydroserver.http import HydroServerHttpRequest
from etl.schemas import DataSourceGetResponse, DataSourcePostBody, DataSourcePatchBody
from etl.services import DataSourceService

data_source_router = Router(tags=["Data Sources"])
data_source_service = DataSourceService()


@data_source_router.get(
    "",
    auth=[session_auth, bearer_auth, apikey_auth],
    response={
        200: list[DataSourceGetResponse],
        401: str,
    },
    by_alias=True,
)
def get_data_sources(
    request: HydroServerHttpRequest,
    workspace_id: Optional[uuid.UUID] = None,
    orchestration_system_id: Optional[uuid.UUID] = None,
):
    """
    Get public Data Sources and Data Sources associated with the authenticated user.
    """

    return 200, data_source_service.list(
        principal=request.principal,
        workspace_id=workspace_id,
        orchestration_system_id=orchestration_system_id,
    )


@data_source_router.post(
    "",
    auth=[session_auth, bearer_auth, apikey_auth],
    response={
        201: DataSourceGetResponse,
        400: str,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True,
)
@transaction.atomic
def create_data_source(request: HydroServerHttpRequest, data: DataSourcePostBody):
    """
    Create a new Data Source.
    """

    return 201, data_source_service.create(principal=request.principal, data=data)


@data_source_router.get(
    "/{data_source_id}",
    auth=[session_auth, bearer_auth, apikey_auth],
    response={
        200: DataSourceGetResponse,
        401: str,
        403: str,
    },
    by_alias=True,
    exclude_unset=True,
)
def get_data_source(request: HydroServerHttpRequest, data_source_id: Path[uuid.UUID]):
    """
    Get a Data Source.
    """

    return 200, data_source_service.get(principal=request.principal, uid=data_source_id)


@data_source_router.patch(
    "/{data_source_id}",
    auth=[session_auth, bearer_auth, apikey_auth],
    response={
        200: DataSourceGetResponse,
        400: str,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True,
)
@transaction.atomic
def update_data_source(
    request: HydroServerHttpRequest,
    data_source_id: Path[uuid.UUID],
    data: DataSourcePatchBody,
):
    """
    Update a Data Source.
    """

    return 200, data_source_service.update(
        principal=request.principal, uid=data_source_id, data=data
    )


@data_source_router.delete(
    "/{data_source_id}",
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
def delete_data_source(
    request: HydroServerHttpRequest, data_source_id: Path[uuid.UUID]
):
    """
    Delete a Data Source.
    """

    return 204, data_source_service.delete(
        principal=request.principal, uid=data_source_id
    )


@data_source_router.post(
    "/{data_source_id}/datastreams/{datastream_id}",
    auth=[session_auth, bearer_auth, apikey_auth],
    response={
        201: str,
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
    data_source_id: Path[uuid.UUID],
    datastream_id: Path[uuid.UUID],
):
    """
    Link a Datastream to a Data Source.
    """

    return 201, data_source_service.link_datastream(
        principal=request.principal, uid=data_source_id, datastream_id=datastream_id
    )


@data_source_router.delete(
    "/{data_source_id}/datastreams/{datastream_id}",
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
def unlink_datastream(
    request: HydroServerHttpRequest,
    data_source_id: Path[uuid.UUID],
    datastream_id: Path[uuid.UUID],
):
    """
    Unlink a Datastream from a Data Source.
    """

    return 204, data_source_service.unlink_datastream(
        principal=request.principal, uid=data_source_id, datastream_id=datastream_id
    )
