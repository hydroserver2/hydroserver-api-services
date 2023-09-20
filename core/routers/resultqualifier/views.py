from ninja import Router, Path
from typing import List
from uuid import UUID
from django.db import transaction, IntegrityError
from accounts.auth.jwt import JWTAuth
from accounts.auth.basic import BasicAuth
from core.models import ResultQualifier
from .schemas import ResultQualifierGetResponse, ResultQualifierPostBody, ResultQualifierPatchBody, \
    ResultQualifierFields
from .utils import query_result_qualifiers, get_result_qualifier_by_id, build_result_qualifier_response


router = Router(tags=['Result Qualifiers'])


@router.get(
    '',
    auth=[JWTAuth(), BasicAuth()],
    response={
        200: List[ResultQualifierGetResponse]
    },
    by_alias=True
)
def get_result_qualifiers(request):
    """
    Get a list of Result Qualifiers

    This endpoint returns a list of Result Qualifiers owned by the authenticated user.
    """

    result_qualifier_query, _ = query_result_qualifiers(
        user=getattr(request, 'authenticated_user', None),
        require_ownership=True
    )

    return [
        build_result_qualifier_response(result_qualifier) for result_qualifier in result_qualifier_query.all()
    ]


@router.get(
    '{result_qualifier_id}',
    auth=[JWTAuth(), BasicAuth()],
    response={
        200: ResultQualifierGetResponse,
        404: str
    },
    by_alias=True
)
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


@router.post(
    '',
    auth=[JWTAuth(), BasicAuth()],
    response={
        201: ResultQualifierGetResponse,
        401: str,
        500: str
    },
    by_alias=True
)
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


@router.patch(
    '{result_qualifier_id}',
    auth=[JWTAuth(), BasicAuth()],
    response={
        203: ResultQualifierGetResponse,
        401: str,
        403: str,
        404: str,
        500: str
    },
    by_alias=True
)
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


@router.delete(
    '{result_qualifier_id}',
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
