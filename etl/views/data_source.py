import uuid
from typing import Optional
from ninja import Router, Path, Query
from django.http import HttpResponse
from django.db import transaction
from hydroserver.security import bearer_auth, session_auth, apikey_auth
from hydroserver.http import HydroServerHttpRequest
from etl.schemas import (
    DataSourceSummaryResponse,
    DataSourceDetailResponse,
    DataSourcePostBody,
    DataSourcePatchBody,
    OrchestrationConfigurationQueryParameters,
)
from etl.services import DataSourceService

data_source_router = Router(tags=["Data Sources"])
data_source_service = DataSourceService()


@data_source_router.get(
    "",
    auth=[session_auth, bearer_auth, apikey_auth],
    response={
        200: list[DataSourceSummaryResponse] | list[DataSourceDetailResponse],
        401: str,
    },
    by_alias=True,
)
def get_data_sources(
    request: HydroServerHttpRequest,
    response: HttpResponse,
    query: Query[OrchestrationConfigurationQueryParameters],
):
    """
    Get public Data Sources and Data Sources associated with the authenticated user.
    """

    return 200, data_source_service.list(
        principal=request.principal,
        response=response,
        page=query.page,
        page_size=query.page_size,
        order_by=query.order_by,
        filtering=query.dict(exclude_unset=True),
        expand_related=query.expand_related,
    )


@data_source_router.post(
    "",
    auth=[session_auth, bearer_auth, apikey_auth],
    response={
        201: DataSourceSummaryResponse | DataSourceDetailResponse,
        400: str,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True,
)
@transaction.atomic
def create_data_source(
    request: HydroServerHttpRequest,
    data: DataSourcePostBody,
    expand_related: Optional[bool] = None,
):
    """
    Create a new Data Source.
    """

    return 201, data_source_service.create(
        principal=request.principal, data=data, expand_related=expand_related
    )


@data_source_router.get(
    "/{data_source_id}",
    auth=[session_auth, bearer_auth, apikey_auth],
    response={
        200: DataSourceSummaryResponse | DataSourceDetailResponse,
        401: str,
        403: str,
    },
    by_alias=True,
    exclude_unset=True,
)
def get_data_source(
    request: HydroServerHttpRequest,
    data_source_id: Path[uuid.UUID],
    expand_related: Optional[bool] = None,
):
    """
    Get a Data Source.
    """

    return 200, data_source_service.get(
        principal=request.principal, uid=data_source_id, expand_related=expand_related
    )


@data_source_router.patch(
    "/{data_source_id}",
    auth=[session_auth, bearer_auth, apikey_auth],
    response={
        200: DataSourceSummaryResponse | DataSourceDetailResponse,
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
    expand_related: Optional[bool] = None,
):
    """
    Update a Data Source.
    """

    return 200, data_source_service.update(
        principal=request.principal,
        uid=data_source_id,
        data=data,
        expand_related=expand_related,
    )


@data_source_router.delete(
    "/{data_source_id}",
    auth=[session_auth, bearer_auth, apikey_auth],
    response={
        204: None,
        401: str,
        403: str,
        409: str,
    },
    by_alias=True,
)
@transaction.atomic
def delete_data_source(
    request: HydroServerHttpRequest,
    data_source_id: Path[uuid.UUID],
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
        204: None,
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
