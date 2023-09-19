from ninja import Router
from typing import List
from uuid import UUID
from django.db import transaction
from accounts.auth.jwt import JWTAuth
from accounts.auth.basic import BasicAuth
from core.models import ObservedProperty
from .schemas import ObservedPropertyGetResponse, ObservedPropertyPostBody, ObservedPropertyPatchBody, \
    ObservedPropertyFields
from .utils import query_observed_properties, get_observed_property_by_id


router = Router(tags=['Observed Properties'])


@router.get(
    '',
    auth=[JWTAuth(), BasicAuth()],
    response={
        200: List[ObservedPropertyGetResponse]
    },
    by_alias=True
)
def get_observed_properties(request):
    """
    Get a list of Observed Properties

    This endpoint returns a list of Observed Properties owned by the authenticated user.
    """

    observed_properties = query_observed_properties(
        user=getattr(request, 'authenticated_user', None)
    )

    return observed_properties


@router.get(
    '{observed_property_id}',
    auth=[JWTAuth(), BasicAuth()],
    response={
        200: ObservedPropertyGetResponse,
        404: str
    },
    by_alias=True
)
def get_observed_property(request, observed_property_id: UUID):
    """
    Get details for an Observed Property

    This endpoint returns details for an Observed Property given an Observed Property ID.
    """

    observed_property = get_observed_property_by_id(
        user=request.authenticated_user,
        observed_property_id=observed_property_id
    )

    if not observed_property:
        return 404, f'Observed Property with ID: {observed_property_id} was not found.'

    return 200, observed_property


@router.post(
    '',
    auth=[JWTAuth(), BasicAuth()],
    response={
        201: ObservedPropertyGetResponse,
        401: str,
        500: str
    },
    by_alias=True
)
@transaction.atomic
def create_observed_property(request, data: ObservedPropertyPostBody):
    """
    Create an Observed Property

    This endpoint will create a new Observed Property owned by the authenticated user and returns the created Observed
    Property.
    """

    observed_property = ObservedProperty.objects.create(
        person=request.authenticated_user,
        **data.dict(include=set(ObservedPropertyFields.__fields__.keys()))
    )

    observed_property = get_observed_property_by_id(
        user=request.authenticated_user,
        observed_property_id=observed_property.id
    )

    if not observed_property:
        return 500, 'Encountered an unexpected error creating Observed Property.'

    return 201, observed_property


@router.patch(
    '{observed_property_id}',
    auth=[JWTAuth(), BasicAuth()],
    response={
        203: ObservedPropertyGetResponse,
        401: str,
        403: str,
        404: str,
        500: str
    },
    by_alias=True
)
@transaction.atomic
def update_observed_property(request, observed_property_id: UUID, data: ObservedPropertyPatchBody):
    """
    Update an Observed Property

    This endpoint will update an existing Observed Property owned by the authenticated user and return the updated
    Observed Property.
    """

    observed_property = ObservedProperty.objects.select_related('person').get(pk=observed_property_id)

    if not observed_property:
        return 404, f'Observed Property with ID: {observed_property_id} was not found.'

    if observed_property.person != request.authenticated_user:
        return 403, 'You do not have permission to modify this Observed Property.'

    observed_property_data = data.dict(include=set(ObservedPropertyFields.__fields__.keys()), exclude_unset=True)

    for field, value in observed_property_data.items():
        setattr(observed_property, field, value)

    observed_property.save()

    observed_property_response = get_observed_property_by_id(
        user=request.authenticated_user,
        observed_property_id=observed_property.id
    )

    if not observed_property_response:
        return 500, 'Encountered an unexpected error updating Observed Property.'

    return 203, observed_property_response


@router.delete(
    '{observed_property_id}',
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
def delete_observed_property(request, observed_property_id: UUID):
    """
    Delete an Observed Property

    This endpoint will delete an existing Observed Property if the authenticated user is the primary owner of the
    Observed Property.
    """

    observed_property = ObservedProperty.objects.select_related('person').get(pk=observed_property_id)

    if not observed_property:
        return 404, f'Observed Property with ID: {observed_property_id} was not found.'

    if observed_property.person != request.authenticated_user:
        return 403, 'You do not have permission to delete this Observed Property.'

    try:
        observed_property.delete()
    except Exception as e:
        return 500, str(e)

    return 204, None
