from ninja.errors import HttpError
from typing import List, Optional
from uuid import UUID
from django.db.models import Q
from django.db.models.query import QuerySet
from core.models import Person, ProcessingLevel
from .schemas import ProcessingLevelFields


def apply_processing_level_auth_rules(
        user: Person,
        processing_level_query: QuerySet,
        require_ownership: bool = False,
        check_result: bool = False
) -> (QuerySet, bool):

    result_exists = processing_level_query.exists() if check_result is True else None

    if not user and require_ownership is True:
        raise HttpError(403, 'You are not authorized to access this Processing Level.')

    if user and require_ownership is True:
        processing_level_query = processing_level_query.filter(Q(person=user))

    return processing_level_query, result_exists


def query_processing_levels(
        user: Person,
        check_result_exists: bool = False,
        require_ownership: bool = False,
        processing_level_ids: Optional[List[UUID]] = None,
        datastream_ids: Optional[List[UUID]] = None
):

    processing_level_query = ProcessingLevel.objects

    if processing_level_ids:
        processing_level_query = processing_level_query.filter(id__in=processing_level_ids)

    if datastream_ids:
        processing_level_query = processing_level_query.filter(datastreams__id__in=datastream_ids)

    processing_level_query, result_exists = apply_processing_level_auth_rules(
        user=user,
        processing_level_query=processing_level_query,
        require_ownership=require_ownership,
        check_result=check_result_exists
    )

    return processing_level_query, result_exists


def check_processing_level_by_id(
        user: Person,
        processing_level_id: UUID,
        require_ownership: bool = False,
        raise_http_errors: bool = False
):

    processing_level_query, processing_level_exists = query_processing_levels(
        user=user,
        processing_level_ids=[processing_level_id],
        require_ownership=require_ownership,
        check_result_exists=True
    )

    processing_level = processing_level_query.exists()

    if raise_http_errors and not processing_level_exists:
        raise HttpError(404, 'ProcessingLevel not found.')
    if raise_http_errors and processing_level_exists and not processing_level:
        raise HttpError(403, 'You do not have permission to perform this action on this Processing Level.')

    return processing_level


def get_processing_level_by_id(
        user: Person,
        processing_level_id: UUID,
        require_ownership: bool = False,
        raise_http_errors: bool = False
):

    processing_level_query, processing_level_exists = query_processing_levels(
        user=user,
        processing_level_ids=[processing_level_id],
        require_ownership=require_ownership,
        check_result_exists=True
    )

    processing_level = next(iter(processing_level_query.all()), None)

    if raise_http_errors and not processing_level_exists:
        raise HttpError(404, 'Processing Level not found.')
    if raise_http_errors and processing_level_exists and not processing_level:
        raise HttpError(403, 'You do not have permission to perform this action on this Processing Level.')

    return processing_level


def build_processing_level_response(processing_level):
    return {
        'id': processing_level.id,
        **{field: getattr(processing_level, field) for field in ProcessingLevelFields.__fields__.keys()},
    }
