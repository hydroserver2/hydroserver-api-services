from ninja import Path
from uuid import UUID
from typing import Optional
from django.db import transaction, IntegrityError
from core.router import DataManagementRouter
from core.models import ResultQualifier
from .schemas import ResultQualifierGetResponse, ResultQualifierPostBody, ResultQualifierPatchBody, \
    ResultQualifierFields
from .utils import query_result_qualifiers, get_result_qualifier_by_id, build_result_qualifier_response


router = DataManagementRouter(tags=['Result Qualifiers'])


@router.dm_list('', response=ResultQualifierGetResponse)
def get_result_qualifiers(request, owned: Optional[bool] = None):
    """
    Get a list of Result Qualifiers

    This endpoint returns a list of Result Qualifiers owned by the authenticated user.
    """

    result_qualifier_query, _ = query_result_qualifiers(
        user=getattr(request, 'authenticated_user', None),
        require_ownership=True if owned is True else False,
        require_ownership_or_unowned=True if owned is None else False,
        raise_http_errors=False
    )

    return [
        build_result_qualifier_response(result_qualifier) for result_qualifier in result_qualifier_query.all()
        if owned is None or owned is True or (owned is False and result_qualifier.person is None)
    ]


@router.dm_get('{result_qualifier_id}', response=ResultQualifierGetResponse)
def get_result_qualifier(request, result_qualifier_id: UUID = Path(...)):
    """
    Get details for a Result Qualifier

    This endpoint returns details for a Result Qualifier given a Result Qualifier ID.
    """

    result_qualifier = get_result_qualifier_by_id(
        user=request.authenticated_user,
        result_qualifier_id=result_qualifier_id,
        raise_http_errors=True
    )

    return 200, build_result_qualifier_response(result_qualifier)


@router.dm_post('', response=ResultQualifierGetResponse)
@transaction.atomic
def create_result_qualifier(request, data: ResultQualifierPostBody):
    """
    Create a Result Qualifier

    This endpoint will create a new Result Qualifier owned by the authenticated user and returns the created Processing
    Level.
    """

    result_qualifier = ResultQualifier.objects.create(
        person=request.authenticated_user,
        **data.dict(include=set(ResultQualifierFields.__fields__.keys()))
    )

    result_qualifier = get_result_qualifier_by_id(
        user=request.authenticated_user,
        result_qualifier_id=result_qualifier.id,
        raise_http_errors=True
    )

    return 201, build_result_qualifier_response(result_qualifier)


@router.dm_patch('{result_qualifier_id}', response=ResultQualifierGetResponse)
@transaction.atomic
def update_result_qualifier(request, data: ResultQualifierPatchBody, result_qualifier_id: UUID = Path(...)):
    """
    Update a Result Qualifier

    This endpoint will update an existing Result Qualifier owned by the authenticated user and return the updated
    Result Qualifier.
    """

    result_qualifier = get_result_qualifier_by_id(
        user=request.authenticated_user,
        result_qualifier_id=result_qualifier_id,
        require_ownership=True,
        raise_http_errors=True
    )

    result_qualifier_data = data.dict(include=set(ResultQualifierFields.__fields__.keys()), exclude_unset=True)

    for field, value in result_qualifier_data.items():
        setattr(result_qualifier, field, value)

    result_qualifier.save()

    result_qualifier = get_result_qualifier_by_id(
        user=request.authenticated_user,
        result_qualifier_id=result_qualifier_id
    )

    return 203, build_result_qualifier_response(result_qualifier)


@router.dm_delete('{result_qualifier_id}')
@transaction.atomic
def delete_result_qualifier(request, result_qualifier_id: UUID = Path(...)):
    """
    Delete a Result Qualifier

    This endpoint will delete an existing Result Qualifier if the authenticated user is the primary owner of the
    Result Qualifier.
    """

    result_qualifier = get_result_qualifier_by_id(
        user=request.authenticated_user,
        result_qualifier_id=result_qualifier_id,
        require_ownership=True,
        raise_http_errors=True
    )

    try:
        result_qualifier.delete()
    except IntegrityError as e:
        return 409, str(e)

    return 204, None
