from ninja import Router
from typing import List
from uuid import UUID
from django.db import transaction
from accounts.auth.jwt import JWTAuth
from accounts.auth.basic import BasicAuth
from core.models import Unit
from .schemas import UnitGetResponse, UnitPostBody, UnitPatchBody, UnitFields
from .utils import query_units, get_unit_by_id


router = Router(tags=['Units'])


@router.get(
    '',
    auth=[JWTAuth(), BasicAuth()],
    response={
        200: List[UnitGetResponse]
    },
    by_alias=True
)
def get_units(request):
    """
    Get a list of Units

    This endpoint returns a list of Units owned by the authenticated user.
    """

    units = query_units(
        user=getattr(request, 'authenticated_user', None)
    )

    return units


@router.get(
    '{unit_id}',
    auth=[JWTAuth(), BasicAuth()],
    response={
        200: UnitGetResponse,
        404: str
    },
    by_alias=True
)
def get_unit(request, unit_id: UUID):
    """
    Get details for a Unit

    This endpoint returns details for a Unit given a Unit ID.
    """

    unit = get_unit_by_id(user=request.authenticated_user, unit_id=unit_id)

    if not unit:
        return 404, f'Unit with ID: {unit_id} was not found.'

    return 200, unit


@router.post(
    '',
    auth=[JWTAuth(), BasicAuth()],
    response={
        201: UnitGetResponse,
        401: str,
        500: str
    },
    by_alias=True
)
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

    unit = get_unit_by_id(user=request.authenticated_user, unit_id=unit.id)

    if not unit:
        return 500, 'Encountered an unexpected error creating Unit.'

    return 201, unit


@router.patch(
    '{unit_id}',
    auth=[JWTAuth(), BasicAuth()],
    response={
        203: UnitGetResponse,
        401: str,
        403: str,
        404: str,
        500: str
    },
    by_alias=True
)
@transaction.atomic
def update_unit(request, unit_id: UUID, data: UnitPatchBody):
    """
    Update a Unit

    This endpoint will update an existing Unit owned by the authenticated user and return the updated Unit.
    """

    unit = Unit.objects.select_related('person').get(pk=unit_id)

    if not unit:
        return 404, f'Unit with ID: {unit_id} was not found.'

    if unit.person != request.authenticated_user:
        return 403, 'You do not have permission to modify this Unit.'

    unit_data = data.dict(include=set(UnitFields.__fields__.keys()), exclude_unset=True)

    for field, value in unit_data.items():
        setattr(unit, field, value)

    unit.save()

    unit_response = get_unit_by_id(user=request.authenticated_user, unit_id=unit.id)

    if not unit_response:
        return 500, 'Encountered an unexpected error updating Unit.'

    return 203, unit_response


@router.delete(
    '{unit_id}',
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
def delete_unit(request, unit_id: UUID):
    """
    Delete a Unit

    This endpoint will delete an existing Unit if the authenticated user is the primary owner of the Unit.
    """

    unit = Unit.objects.select_related('person').get(pk=unit_id)

    if not unit:
        return 404, f'Unit with ID: {unit_id} was not found.'

    if unit.person != request.authenticated_user:
        return 403, 'You do not have permission to delete this Unit.'

    try:
        unit.delete()
    except Exception as e:
        return 500, str(e)

    return 204, None
