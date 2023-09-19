from ninja import Router
from typing import List
from uuid import UUID
from django.db import transaction
from accounts.auth.jwt import JWTAuth
from accounts.auth.basic import BasicAuth
from core.models import ProcessingLevel
from .schemas import ProcessingLevelGetResponse, ProcessingLevelPostBody, ProcessingLevelPatchBody, \
    ProcessingLevelFields
from .utils import query_processing_levels, get_processing_level_by_id


router = Router(tags=['Processing Levels'])


@router.get(
    '',
    auth=[JWTAuth(), BasicAuth()],
    response={
        200: List[ProcessingLevelGetResponse]
    },
    by_alias=True
)
def get_processing_levels(request):
    """
    Get a list of Processing Levels

    This endpoint returns a list of Processing Levels owned by the authenticated user.
    """

    processing_levels = query_processing_levels(
        user=getattr(request, 'authenticated_user', None)
    )

    return processing_levels


@router.get(
    '{processing_level_id}',
    auth=[JWTAuth(), BasicAuth()],
    response={
        200: ProcessingLevelGetResponse,
        404: str
    },
    by_alias=True
)
def get_processing_level(request, processing_level_id: UUID):
    """
    Get details for a Processing Level

    This endpoint returns details for a Processing Level given a Processing Level ID.
    """

    processing_level = get_processing_level_by_id(
        user=request.authenticated_user,
        processing_level_id=processing_level_id
    )

    if not processing_level:
        return 404, f'Processing Level with ID: {processing_level_id} was not found.'

    return 200, processing_level


@router.post(
    '',
    auth=[JWTAuth(), BasicAuth()],
    response={
        201: ProcessingLevelGetResponse,
        401: str,
        500: str
    },
    by_alias=True
)
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
        processing_level_id=processing_level.id
    )

    if not processing_level:
        return 500, 'Encountered an unexpected error creating Processing Level.'

    return 201, processing_level


@router.patch(
    '{processing_level_id}',
    auth=[JWTAuth(), BasicAuth()],
    response={
        203: ProcessingLevelGetResponse,
        401: str,
        403: str,
        404: str,
        500: str
    },
    by_alias=True
)
@transaction.atomic
def update_processing_level(request, processing_level_id: UUID, data: ProcessingLevelPatchBody):
    """
    Update a Processing Level

    This endpoint will update an existing Processing Level owned by the authenticated user and return the updated
    Processing Level.
    """

    processing_level = ProcessingLevel.objects.select_related('person').get(pk=processing_level_id)

    if not processing_level:
        return 404, f'Processing Level with ID: {processing_level_id} was not found.'

    if processing_level.person != request.authenticated_user:
        return 403, 'You do not have permission to modify this Processing Level.'

    processing_level_data = data.dict(include=set(ProcessingLevelFields.__fields__.keys()), exclude_unset=True)

    for field, value in processing_level_data.items():
        setattr(processing_level, field, value)

    processing_level.save()

    processing_level_response = get_processing_level_by_id(
        user=request.authenticated_user,
        processing_level_id=processing_level.id
    )

    if not processing_level_response:
        return 500, 'Encountered an unexpected error updating Processing Level.'

    return 203, processing_level_response


@router.delete(
    '{processing_level_id}',
    auth=[JWTAuth(), BasicAuth()],
    response={
        204: None,
        401: str,
        403: str,
        404: str,
        500: str
    }
)
@transaction.atomic
def delete_processing_level(request, processing_level_id: UUID):
    """
    Delete a Processing Level

    This endpoint will delete an existing Processing Level if the authenticated user is the primary owner of the
    Processing Level.
    """

    processing_level = ProcessingLevel.objects.select_related('person').get(pk=processing_level_id)

    if not processing_level:
        return 404, f'Processing Level with ID: {processing_level_id} was not found.'

    if processing_level.person != request.authenticated_user:
        return 403, 'You do not have permission to delete this Processing Level.'

    try:
        processing_level.delete()
    except Exception as e:
        return 500, str(e)

    return 204, None
