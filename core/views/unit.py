from ninja import Path
from uuid import UUID
from typing import Optional
from django.db import transaction, IntegrityError
from django.db.models import Q
from core.router import DataManagementRouter
from core.models import Unit
from core.schemas.base import metadataOwnerOptions
from core.schemas.unit import UnitGetResponse, UnitPostBody, UnitPatchBody, UnitFields


router = DataManagementRouter(tags=['Units'])


@router.dm_list('', response=UnitGetResponse)
def get_units(request, owner: Optional[metadataOwnerOptions] = 'anyUserOrNoUser'):
    """
    Get a list of Units

    This endpoint returns a list of Units owned by the authenticated user.
    """

    unit_query = Unit.objects.select_related('person')
    unit_query = unit_query.filter(Q(person__isnull=True) | Q(person__is_active=True))

    if owner == 'currentUser':
        unit_query = unit_query.filter(Q(person__isnull=False) & Q(person=request.authenticated_user))
    elif owner == 'noUser':
        unit_query = unit_query.filter(person__isnull=True)
    elif owner == 'currentUserOrNoUser':
        unit_query = unit_query.filter(Q(person__isnull=True) | Q(person=request.authenticated_user))
    elif owner == 'anyUser':
        unit_query = unit_query.filter(person__isnull=False)

    unit_query = unit_query.distinct()

    response = [
        UnitGetResponse.serialize(unit) for unit in unit_query.all()
    ]

    return 200, response


@router.dm_get('{unit_id}', response=UnitGetResponse)
def get_unit(request, unit_id: UUID = Path(...)):
    """
    Get details for a Unit

    This endpoint returns details for a Unit given a Unit ID.
    """

    unit = Unit.objects.get_by_id(unit_id, request.authenticated_user, method='GET', raise_404=True)

    return 200, UnitGetResponse.serialize(unit)


@router.dm_post('', response=UnitGetResponse)
@transaction.atomic
def create_unit(request, data: UnitPostBody):
    """
    Create a Unit

    This endpoint will create a new Unit owned by the authenticated user and returns the created Unit.
    """

    unit = Unit.objects.create(
        person=request.authenticated_user,
        **data.dict(include=set(UnitFields.__fields__.keys()))
    )

    return 201, UnitGetResponse.serialize(unit)


@router.dm_patch('{unit_id}', response=UnitGetResponse)
@transaction.atomic
def update_unit(request, data: UnitPatchBody, unit_id: UUID = Path(...)):
    """
    Update a Unit

    This endpoint will update an existing Unit owned by the authenticated user and return the updated Unit.
    """

    unit = Unit.objects.get_by_id(unit_id, request.authenticated_user, method='PATCH', raise_404=True)
    unit_data = data.dict(include=set(UnitFields.__fields__.keys()), exclude_unset=True)

    if not request.authenticated_user.permissions.check_allowed_fields(
            'Unit', fields=[*unit_data.keys()]
    ):
        return 403, 'You do not have permission to modify all the given fields of this Unit.'

    for field, value in unit_data.items():
        setattr(unit, field, value)

    unit.save()

    return 203, UnitGetResponse.serialize(unit)


@router.dm_delete('{unit_id}')
@transaction.atomic
def delete_unit(request, unit_id: UUID = Path(...)):
    """
    Delete a Unit

    This endpoint will delete an existing Unit if the authenticated user is the primary owner of the Unit.
    """

    unit = Unit.objects.get_by_id(unit_id, request.authenticated_user, method='DELETE', raise_404=True)

    try:
        unit.delete()
    except IntegrityError as e:
        return 409, str(e)

    return 204, None
