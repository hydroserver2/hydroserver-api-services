import uuid
from ninja import Router, Path, Query
from django.http import HttpResponse
from django.db import transaction
from hydroserver.security import bearer_auth, session_auth, apikey_auth
from hydroserver.http import HydroServerHttpRequest
from etl.schemas import (
    DataArchiveSummaryResponse,
    DataArchiveDetailResponse,
    DataArchivePostBody,
    DataArchivePatchBody,
    OrchestrationConfigurationQueryParameters,
)
from etl.services import DataArchiveService

data_archive_router = Router(tags=["Data Archives"])
data_archive_service = DataArchiveService()


@data_archive_router.get(
    "",
    auth=[session_auth, bearer_auth, apikey_auth],
    response={
        200: list[DataArchiveDetailResponse],
        401: str,
    },
    by_alias=True,
)
def get_data_archives(
    request: HydroServerHttpRequest,
    response: HttpResponse,
    query: Query[OrchestrationConfigurationQueryParameters],
):
    """
    Get public Data Archives and Data Archives associated with the authenticated user.
    """

    return 200, data_archive_service.list(
        principal=request.principal,
        response=response,
        page=query.page,
        page_size=query.page_size,
        order_by=query.order_by,
        filtering=query.dict(exclude_unset=True),
    )


@data_archive_router.post(
    "",
    auth=[session_auth, bearer_auth, apikey_auth],
    response={
        201: DataArchiveSummaryResponse,
        400: str,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True,
)
@transaction.atomic
def create_data_archive(request: HydroServerHttpRequest, data: DataArchivePostBody):
    """
    Create a new Data Archive.
    """

    return 201, data_archive_service.create(principal=request.principal, data=data)


@data_archive_router.get(
    "/{data_archive_id}",
    auth=[session_auth, bearer_auth, apikey_auth],
    response={
        200: DataArchiveDetailResponse,
        401: str,
        403: str,
    },
    by_alias=True,
    exclude_unset=True,
)
def get_data_archive(request: HydroServerHttpRequest, data_archive_id: Path[uuid.UUID]):
    """
    Get a Data Archive.
    """

    return 200, data_archive_service.get(
        principal=request.principal, uid=data_archive_id
    )


@data_archive_router.patch(
    "/{data_archive_id}",
    auth=[session_auth, bearer_auth, apikey_auth],
    response={
        200: DataArchiveSummaryResponse,
        400: str,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True,
)
@transaction.atomic
def update_data_archive(
    request: HydroServerHttpRequest,
    data_archive_id: Path[uuid.UUID],
    data: DataArchivePatchBody,
):
    """
    Update a Data Archive.
    """

    return 200, data_archive_service.update(
        principal=request.principal, uid=data_archive_id, data=data
    )


@data_archive_router.delete(
    "/{data_archive_id}",
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
def delete_data_archive(
    request: HydroServerHttpRequest, data_archive_id: Path[uuid.UUID]
):
    """
    Delete a Data Archive.
    """

    return 204, data_archive_service.delete(
        principal=request.principal, uid=data_archive_id
    )


@data_archive_router.post(
    "/{data_archive_id}/datastreams/{datastream_id}",
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
    data_archive_id: Path[uuid.UUID],
    datastream_id: Path[uuid.UUID],
):
    """
    Link a Datastream to a Data Archive.
    """

    return 201, data_archive_service.link_datastream(
        principal=request.principal,
        uid=data_archive_id,
        datastream_id=datastream_id,
    )


@data_archive_router.delete(
    "/{data_archive_id}/datastreams/{datastream_id}",
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
    data_archive_id: Path[uuid.UUID],
    datastream_id: Path[uuid.UUID],
):
    """
    Unlink a Datastream from a Data Archive.
    """

    return 204, data_archive_service.unlink_datastream(
        principal=request.principal,
        uid=data_archive_id,
        datastream_id=datastream_id,
    )
