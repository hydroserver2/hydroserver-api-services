from ninja import Router, Path
from typing import List
from uuid import UUID
from django.db import transaction, IntegrityError
from accounts.auth.jwt import JWTAuth
from accounts.auth.basic import BasicAuth
from core.models import Unit
from .schemas import UnitGetResponse, UnitPostBody, UnitPatchBody, UnitFields
from .utils import query_units, get_unit_by_id, build_unit_response


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

    unit_query, _ = query_units(
        user=getattr(request, 'authenticated_user', None),
        require_ownership=True
    )

    return [
        build_unit_response(unit) for unit in unit_query.all()
    ]


@router.get(
    '{unit_id}',
    auth=[JWTAuth(), BasicAuth()],
    response={
        200: UnitGetResponse,
        404: str
    },
    by_alias=True
)
def get_unit(request, unit_id: UUID = Path(...)):
    """
    Get details for a Unit

    This endpoint returns details for a Unit given a Unit ID.
    """

    unit = get_unit_by_id(user=request.authenticated_user, unit_id=unit_id, raise_http_errors=True)

    return 200, build_unit_response(unit)


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

    unit = get_unit_by_id(user=request.authenticated_user, unit_id=unit.id, raise_http_errors=True)

    return 201, build_unit_response(unit)


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
def update_unit(request, data: UnitPatchBody, unit_id: UUID = Path(...)):
    """
    Update a Unit

    This endpoint will update an existing Unit owned by the authenticated user and return the updated Unit.
    """

    unit = get_unit_by_id(
        user=request.authenticated_user,
        unit_id=unit_id,
        require_ownership=True,
        raise_http_errors=True
    )

    unit_data = data.dict(include=set(UnitFields.__fields__.keys()), exclude_unset=True)

    for field, value in unit_data.items():
        setattr(unit, field, value)

    unit.save()

    unit = get_unit_by_id(user=request.authenticated_user, unit_id=unit_id)

    return 203, build_unit_response(unit)


@router.delete(
    '{unit_id}',
    auth=[JWTAuth(), BasicAuth()],
    response={
        204: None,
        401: str,
        403: str,
        404: str,
        409: str
    }
)
@transaction.atomic
def delete_unit(request, unit_id: UUID = Path(...)):
    """
    Delete a Unit

    This endpoint will delete an existing Unit if the authenticated user is the primary owner of the Unit.
    """

    unit = get_unit_by_id(
        user=request.authenticated_user,
        unit_id=unit_id,
        require_ownership=True,
        raise_http_errors=True
    )

    try:
        unit.delete()
    except IntegrityError as e:
        return 409, str(e)

    return 204, None
