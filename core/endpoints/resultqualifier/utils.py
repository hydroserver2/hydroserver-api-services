from ninja.errors import HttpError
from typing import List, Optional
from uuid import UUID
from django.db.models import Q
from django.db.models.query import QuerySet
from core.models import Person, ResultQualifier
from .schemas import ResultQualifierFields


def apply_result_qualifier_auth_rules(
        user: Optional[Person],
        result_qualifier_query: QuerySet,
        require_ownership: bool = False,
        require_ownership_or_unowned: bool = False,
        check_result: bool = False
) -> (QuerySet, bool):

    result_exists = result_qualifier_query.exists() if check_result is True else None

    if not user and require_ownership is True:
        raise HttpError(403, 'You are not authorized to access this Result Qualifier.')

    if user and require_ownership is True:
        result_qualifier_query = result_qualifier_query.filter((Q(person=user) & Q(person__is_active=True)))
    elif user and require_ownership_or_unowned is True:
        result_qualifier_query = result_qualifier_query.filter(
            (Q(person=user) & Q(person__is_active=True)) | Q(person=None)
        )
    elif not user and require_ownership_or_unowned is True:
        result_qualifier_query = result_qualifier_query.filter(Q(person=None))

    return result_qualifier_query, result_exists


def query_result_qualifiers(
        user: Optional[Person],
        check_result_exists: bool = False,
        require_ownership: bool = False,
        require_ownership_or_unowned: bool = False,
        result_qualifier_ids: Optional[List[UUID]] = None,
        datastream_ids: Optional[List[UUID]] = None
):

    result_qualifier_query = ResultQualifier.objects

    if result_qualifier_ids:
        result_qualifier_query = result_qualifier_query.filter(id__in=result_qualifier_ids)

    if datastream_ids:
        result_qualifier_query = result_qualifier_query.filter(datastreams__id__in=datastream_ids)

    result_qualifier_query = result_qualifier_query.select_related('person', 'person__organization')

    result_qualifier_query, result_exists = apply_result_qualifier_auth_rules(
        user=user,
        result_qualifier_query=result_qualifier_query,
        require_ownership=require_ownership,
        require_ownership_or_unowned=require_ownership_or_unowned,
        check_result=check_result_exists
    )

    return result_qualifier_query, result_exists


def check_result_qualifier_by_id(
        user: Optional[Person],
        result_qualifier_id: UUID,
        require_ownership: bool = False,
        require_ownership_or_unowned: bool = False,
        raise_http_errors: bool = False
):

    result_qualifier_query, result_qualifier_exists = query_result_qualifiers(
        user=user,
        result_qualifier_ids=[result_qualifier_id],
        require_ownership=require_ownership,
        require_ownership_or_unowned=require_ownership_or_unowned,
        check_result_exists=True
    )

    result_qualifier = result_qualifier_query.exists()

    if raise_http_errors and not result_qualifier_exists:
        raise HttpError(404, 'ResultQualifier not found.')
    if raise_http_errors and result_qualifier_exists and not result_qualifier:
        raise HttpError(403, 'You do not have permission to perform this action on this Result Qualifier.')

    return result_qualifier


def get_result_qualifier_by_id(
        user: Optional[Person],
        result_qualifier_id: UUID,
        require_ownership: bool = False,
        require_ownership_or_unowned: bool = False,
        raise_http_errors: bool = False
):

    result_qualifier_query, result_qualifier_exists = query_result_qualifiers(
        user=user,
        result_qualifier_ids=[result_qualifier_id],
        require_ownership=require_ownership,
        require_ownership_or_unowned=require_ownership_or_unowned,
        check_result_exists=True
    )

    result_qualifier = next(iter(result_qualifier_query.all()), None)

    if raise_http_errors and not result_qualifier_exists:
        raise HttpError(404, 'Result Qualifier not found.')
    if raise_http_errors and result_qualifier_exists and not result_qualifier:
        raise HttpError(403, 'You do not have permission to perform this action on this Result Qualifier.')

    return result_qualifier


def build_result_qualifier_response(result_qualifier):
    return {
        'id': result_qualifier.id,
        'owner': result_qualifier.person.email if result_qualifier.person else None,
        **{field: getattr(result_qualifier, field) for field in ResultQualifierFields.__fields__.keys()},
    }
