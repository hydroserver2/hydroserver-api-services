from ninja import Path
from uuid import UUID
from typing import Optional
from django.db import transaction, IntegrityError
from core.router import DataManagementRouter
from core.models import ProcessingLevel
from .schemas import ProcessingLevelGetResponse, ProcessingLevelPostBody, ProcessingLevelPatchBody, \
    ProcessingLevelFields
from .utils import query_processing_levels, get_processing_level_by_id, build_processing_level_response


router = DataManagementRouter(tags=['Processing Levels'])


@router.dm_list('', response=ProcessingLevelGetResponse)
def get_processing_levels(request, exclude_unowned: Optional[bool] = False):
    """
    Get a list of Processing Levels

    This endpoint returns a list of Processing Levels owned by the authenticated user.
    """

    processing_level_query, _ = query_processing_levels(
        user=getattr(request, 'authenticated_user', None),
        require_ownership=exclude_unowned,
        require_ownership_or_unowned=True,
        raise_http_errors=False
    )

    return [
        build_processing_level_response(processing_level) for processing_level in processing_level_query.all()
    ]


@router.dm_get('{processing_level_id}', response=ProcessingLevelGetResponse)
def get_processing_level(request, processing_level_id: UUID = Path(...)):
    """
    Get details for a Processing Level

    This endpoint returns details for a Processing Level given a Processing Level ID.
    """

    processing_level = get_processing_level_by_id(
        user=request.authenticated_user,
        processing_level_id=processing_level_id,
        raise_http_errors=True
    )

    return 200, build_processing_level_response(processing_level)


@router.dm_post('', response=ProcessingLevelGetResponse)
@transaction.atomic
def create_processing_level(request, data: ProcessingLevelPostBody):
    """
    Create a Processing Level

    This endpoint will create a new Processing Level owned by the authenticated user and returns the created Processing
    Level.
    """

    processing_level = ProcessingLevel.objects.create(
        person=request.authenticated_user,
        **data.dict(include=set(ProcessingLevelFields.__fields__.keys()))
    )

    processing_level = get_processing_level_by_id(
        user=request.authenticated_user,
        processing_level_id=processing_level.id,
        raise_http_errors=True
    )

    return 201, build_processing_level_response(processing_level)


@router.dm_patch('{processing_level_id}', response=ProcessingLevelGetResponse)
@transaction.atomic
def update_processing_level(request, data: ProcessingLevelPatchBody, processing_level_id: UUID = Path(...)):
    """
    Update a Processing Level

    This endpoint will update an existing Processing Level owned by the authenticated user and return the updated
    Processing Level.
    """

    processing_level = get_processing_level_by_id(
        user=request.authenticated_user,
        processing_level_id=processing_level_id,
        require_ownership=True,
        raise_http_errors=True
    )

    processing_level_data = data.dict(include=set(ProcessingLevelFields.__fields__.keys()), exclude_unset=True)

    for field, value in processing_level_data.items():
        setattr(processing_level, field, value)

    processing_level.save()

    processing_level = get_processing_level_by_id(
        user=request.authenticated_user,
        processing_level_id=processing_level_id
    )

    return 203, build_processing_level_response(processing_level)


@router.dm_delete('{processing_level_id}')
@transaction.atomic
def delete_processing_level(request, processing_level_id: UUID = Path(...)):
    """
    Delete a Processing Level

    This endpoint will delete an existing Processing Level if the authenticated user is the primary owner of the
    Processing Level.
    """

    processing_level = get_processing_level_by_id(
        user=request.authenticated_user,
        processing_level_id=processing_level_id,
        require_ownership=True,
        raise_http_errors=True
    )

    try:
        processing_level.delete()
    except IntegrityError as e:
        return 409, str(e)

    return 204, None
