from ninja import Path
from uuid import UUID
from typing import Optional
from django.db import transaction, IntegrityError
from django.db.models import Q
from core.router import DataManagementRouter
from core.models import ObservedProperty
from core.schemas.base import metadataOwnerOptions
from core.schemas.observed_property import ObservedPropertyGetResponse, ObservedPropertyPostBody, \
    ObservedPropertyPatchBody, ObservedPropertyFields


router = DataManagementRouter(tags=['Observed Properties'])


@router.dm_list('', response=ObservedPropertyGetResponse)
def get_observed_properties(request, owner: Optional[metadataOwnerOptions] = 'anyUserOrNoUser'):
    """
    Get a list of Observed Properties

    This endpoint returns a list of observed properties owned by the authenticated user.
    """

    observed_property_query = ObservedProperty.objects.select_related('person')
    observed_property_query = observed_property_query.filter(Q(person__isnull=True) | Q(person__is_active=True))

    if owner == 'currentUser':
        observed_property_query = observed_property_query.filter(
            Q(person__isnull=False) & Q(person=request.authenticated_user)
        )
    elif owner == 'noUser':
        observed_property_query = observed_property_query.filter(person__isnull=True)
    elif owner == 'currentUserOrNoUser':
        observed_property_query = observed_property_query.filter(
            Q(person__isnull=True) | Q(person=request.authenticated_user)
        )
    elif owner == 'anyUser':
        observed_property_query = observed_property_query.filter(person__isnull=False)

    observed_property_query = observed_property_query.distinct()

    response = [
        observed_property.serialize() for observed_property in observed_property_query.all()
    ]

    return 200, response


@router.dm_get('{observed_property_id}', response=ObservedPropertyGetResponse)
def get_observed_property(request, observed_property_id: UUID = Path(...)):
    """
    Get details for an Observed Property

    This endpoint returns details for an observed property given an observed property ID.
    """

    observed_property = ObservedProperty.objects.get_by_id(
        observed_property_id=observed_property_id,
        user=request.authenticated_user,
        method='GET',
        raise_404=True
    )

    return 200, observed_property.serialize()


@router.dm_post('', response=ObservedPropertyGetResponse)
@transaction.atomic
def create_observed_property(request, data: ObservedPropertyPostBody):
    """
    Create an Observed Property

    This endpoint will create a new observed property owned by the authenticated user and returns the created observed
    property.
    """

    observed_property = ObservedProperty.objects.create(
        person=request.authenticated_user,
        **data.dict(include=set(ObservedPropertyFields.__fields__.keys()))
    )

    return 201, observed_property.serialize()


@router.dm_patch('{observed_property_id}', response=ObservedPropertyGetResponse)
@transaction.atomic
def update_observed_property(request, data: ObservedPropertyPatchBody, observed_property_id: UUID = Path(...)):
    """
    Update an Observed Property

    This endpoint will update an existing observed property owned by the authenticated user and return the updated
    observed property.
    """

    observed_property = ObservedProperty.objects.get_by_id(
        observed_property_id=observed_property_id,
        user=request.authenticated_user,
        method='PATCH',
        raise_404=True
    )
    observed_property_data = data.dict(include=set(ObservedPropertyFields.__fields__.keys()), exclude_unset=True)

    if not request.authenticated_user.permissions.check_allowed_fields(
            'ObservedProperty', fields=[*observed_property_data.keys()]
    ):
        return 403, 'You do not have permission to modify all the given fields of this observed property.'

    for field, value in observed_property_data.items():
        setattr(observed_property, field, value)

    observed_property.save()

    return 203, observed_property.serialize()


@router.dm_delete('{observed_property_id}')
@transaction.atomic
def delete_observed_property(request, observed_property_id: UUID = Path(...)):
    """
    Delete an Observed Property

    This endpoint will delete an existing ObservedProperty if the authenticated user is the primary owner of the
    Observed Property.
    """

    observed_property = ObservedProperty.objects.get_by_id(
        observed_property_id=observed_property_id,
        user=request.authenticated_user,
        method='DELETE',
        raise_404=True
    )

    try:
        observed_property.delete()
    except IntegrityError as e:
        return 409, str(e)

    return 204, None
