from ninja import Path
from uuid import UUID
from typing import Optional
from django.db import transaction, IntegrityError
from django.db.models import Q
from core.router import DataManagementRouter
from core.models import ProcessingLevel
from core.schemas.base import metadataOwnerOptions
from core.schemas.processing_level import ProcessingLevelGetResponse, ProcessingLevelPostBody, \
    ProcessingLevelPatchBody, ProcessingLevelFields


router = DataManagementRouter(tags=['Processing Levels'])


@router.dm_list('', response=ProcessingLevelGetResponse)
def get_processing_levels(request, owner: Optional[metadataOwnerOptions] = 'anyUserOrNoUser'):
    """
    Get a list of Processing Levels

    This endpoint returns a list of processing levels owned by the authenticated user.
    """

    processing_level_query = ProcessingLevel.objects.select_related('person')
    processing_level_query = processing_level_query.filter(Q(person__isnull=True) | Q(person__is_active=True))

    if owner == 'currentUser':
        processing_level_query = processing_level_query.filter(
            Q(person__isnull=False) & Q(person=request.authenticated_user)
        )
    elif owner == 'noUser':
        processing_level_query = processing_level_query.filter(person__isnull=True)
    elif owner == 'currentUserOrNoUser':
        processing_level_query = processing_level_query.filter(
            Q(person__isnull=True) | Q(person=request.authenticated_user)
        )
    elif owner == 'anyUser':
        processing_level_query = processing_level_query.filter(person__isnull=False)

    processing_level_query = processing_level_query.distinct()

    response = [
        ProcessingLevelGetResponse.serialize(processing_level) for processing_level in processing_level_query.all()
    ]

    return 200, response


@router.dm_get('{processing_level_id}', response=ProcessingLevelGetResponse)
def get_processing_level(request, processing_level_id: UUID = Path(...)):
    """
    Get details for a Processing Level

    This endpoint returns details for a processing level given a processing level ID.
    """

    processing_level = ProcessingLevel.objects.get_by_id(
        processing_level_id=processing_level_id,
        user=request.authenticated_user,
        method='GET',
        raise_404=True
    )

    return 200, ProcessingLevelGetResponse.serialize(processing_level)


@router.dm_post('', response=ProcessingLevelGetResponse)
@transaction.atomic
def create_processing_level(request, data: ProcessingLevelPostBody):
    """
    Create a Processing Level

    This endpoint will create a new processing level owned by the authenticated user and returns the created processing
    level.
    """

    processing_level = ProcessingLevel.objects.create(
        person=request.authenticated_user,
        **data.dict(include=set(ProcessingLevelFields.__fields__.keys()))
    )

    return 201, ProcessingLevelGetResponse.serialize(processing_level)


@router.dm_patch('{processing_level_id}', response=ProcessingLevelGetResponse)
@transaction.atomic
def update_processing_level(request, data: ProcessingLevelPatchBody, processing_level_id: UUID = Path(...)):
    """
    Update a Processing Level

    This endpoint will update an existing processing level owned by the authenticated user and return the updated
    processing level.
    """

    processing_level = ProcessingLevel.objects.get_by_id(
        processing_level_id=processing_level_id,
        user=request.authenticated_user,
        method='PATCH',
        raise_404=True
    )
    processing_level_data = data.dict(include=set(ProcessingLevelFields.__fields__.keys()), exclude_unset=True)

    if not request.authenticated_user.permissions.check_allowed_fields(
            'ProcessingLevel', fields=[*processing_level_data.keys()]
    ):
        return 403, 'You do not have permission to modify all the given fields of this processing level.'

    for field, value in processing_level_data.items():
        setattr(processing_level, field, value)

    processing_level.save()

    return 203, ProcessingLevelGetResponse.serialize(processing_level)


@router.dm_delete('{processing_level_id}')
@transaction.atomic
def delete_processing_level(request, processing_level_id: UUID = Path(...)):
    """
    Delete a Processing Level

    This endpoint will delete an existing processing level if the authenticated user is the primary owner of the
    processing level.
    """

    processing_level = ProcessingLevel.objects.get_by_id(
        processing_level_id=processing_level_id,
        user=request.authenticated_user,
        method='DELETE',
        raise_404=True
    )

    try:
        processing_level.delete()
    except IntegrityError as e:
        return 409, str(e)

    return 204, None
