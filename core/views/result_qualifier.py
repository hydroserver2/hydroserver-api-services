from ninja import Path
from uuid import UUID
from typing import Optional
from django.db import transaction, IntegrityError
from django.db.models import Q
from core.router import DataManagementRouter
from core.models import ResultQualifier
from core.schemas.base import metadataOwnerOptions
from core.schemas.result_qualifier import ResultQualifierGetResponse, ResultQualifierPostBody, \
    ResultQualifierPatchBody, ResultQualifierFields


router = DataManagementRouter(tags=['Result Qualifiers'])


@router.dm_list('', response=ResultQualifierGetResponse)
def get_result_qualifiers(request, owner: Optional[metadataOwnerOptions] = 'anyUserOrNoUser'):
    """
    Get a list of Result Qualifiers

    This endpoint returns a list of result qualifiers owned by the authenticated user.
    """

    result_qualifier_query = ResultQualifier.objects.select_related('person')
    result_qualifier_query = result_qualifier_query.filter(Q(person__isnull=True) | Q(person__is_active=True))

    if owner == 'currentUser':
        result_qualifier_query = result_qualifier_query.filter(
            Q(person__isnull=False) & Q(person=request.authenticated_user)
        )
    elif owner == 'noUser':
        result_qualifier_query = result_qualifier_query.filter(person__isnull=True)
    elif owner == 'currentUserOrNoUser':
        result_qualifier_query = result_qualifier_query.filter(
            Q(person__isnull=True) | Q(person=request.authenticated_user)
        )
    elif owner == 'anyUser':
        result_qualifier_query = result_qualifier_query.filter(person__isnull=False)

    result_qualifier_query = result_qualifier_query.distinct()

    response = [
        ResultQualifierGetResponse.serialize(result_qualifier) for result_qualifier in result_qualifier_query.all()
    ]

    return 200, response


@router.dm_get('{result_qualifier_id}', response=ResultQualifierGetResponse)
def get_result_qualifier(request, result_qualifier_id: UUID = Path(...)):
    """
    Get details for a Result Qualifier

    This endpoint returns details for a result qualifier given a result qualifier ID.
    """

    result_qualifier = ResultQualifier.objects.get_by_id(
        result_qualifier_id=result_qualifier_id,
        user=request.authenticated_user,
        method='GET',
        raise_404=True
    )

    return 200, ResultQualifierGetResponse.serialize(result_qualifier)


@router.dm_post('', response=ResultQualifierGetResponse)
@transaction.atomic
def create_result_qualifier(request, data: ResultQualifierPostBody):
    """
    Create a Result Qualifier

    This endpoint will create a new result qualifier owned by the authenticated user and returns the created result
    qualifier.
    """

    result_qualifier = ResultQualifier.objects.create(
        person=request.authenticated_user,
        **data.dict(include=set(ResultQualifierFields.__fields__.keys()))
    )

    return 201, ResultQualifierGetResponse.serialize(result_qualifier)


@router.dm_patch('{result_qualifier_id}', response=ResultQualifierGetResponse)
@transaction.atomic
def update_result_qualifier(request, data: ResultQualifierPatchBody, result_qualifier_id: UUID = Path(...)):
    """
    Update a Result Qualifier

    This endpoint will update an existing result qualifier owned by the authenticated user and return the updated
    result qualifier.
    """

    result_qualifier = ResultQualifier.objects.get_by_id(
        result_qualifier_id=result_qualifier_id,
        user=request.authenticated_user,
        method='PATCH',
        raise_404=True
    )
    result_qualifier_data = data.dict(include=set(ResultQualifierFields.__fields__.keys()), exclude_unset=True)

    if not request.authenticated_user.permissions.check_allowed_fields(
            'ResultQualifier', fields=[*result_qualifier_data.keys()]
    ):
        return 403, 'You do not have permission to modify all the given fields of this result qualifier.'

    for field, value in result_qualifier_data.items():
        setattr(result_qualifier, field, value)

    result_qualifier.save()

    return 203, ResultQualifierGetResponse.serialize(result_qualifier)


@router.dm_delete('{result_qualifier_id}')
@transaction.atomic
def delete_result_qualifier(request, result_qualifier_id: UUID = Path(...)):
    """
    Delete a Result Qualifier

    This endpoint will delete an existing result qualifier if the authenticated user is the primary owner of the
    result qualifier.
    """

    result_qualifier = ResultQualifier.objects.get_by_id(
        result_qualifier_id=result_qualifier_id,
        user=request.authenticated_user,
        method='DELETE',
        raise_404=True
    )

    try:
        result_qualifier.delete()
    except IntegrityError as e:
        return 409, str(e)

    return 204, None
