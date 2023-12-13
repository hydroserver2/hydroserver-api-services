from ninja.errors import HttpError
from typing import List, Optional
from uuid import UUID
from django.db.models import Q
from django.db.models.query import QuerySet
from core.models import Person, DataSource
from .schemas import DataSourceFields


def apply_data_source_auth_rules(
        user: Person,
        data_source_query: QuerySet,
        require_ownership: bool = False,
        check_result: bool = False
) -> (QuerySet, bool):

    result_exists = data_source_query.exists() if check_result is True else None

    if not user and require_ownership is True:
        raise HttpError(403, 'You are not authorized to access this Data Source.')

    if user and require_ownership is True:
        data_source_query = data_source_query.filter((Q(person=user) & Q(person__is_active=True)))

    return data_source_query, result_exists


def query_data_sources(
        user: Person,
        check_result_exists: bool = False,
        require_ownership: bool = False,
        data_source_ids: Optional[List[UUID]] = None,
        data_loader_ids: Optional[List[UUID]] = None,
        datastream_ids: Optional[List[UUID]] = None
):

    data_source_query = DataSource.objects

    if data_source_ids:
        data_source_query = data_source_query.filter(id__in=data_source_ids)

    if data_loader_ids:
        data_source_query = data_source_query.filter(data_loader_id__in=data_loader_ids)

    if datastream_ids:
        data_source_query = data_source_query.filter(datastreams__id__in=datastream_ids)

    data_source_query, result_exists = apply_data_source_auth_rules(
        user=user,
        data_source_query=data_source_query,
        require_ownership=require_ownership,
        check_result=check_result_exists
    )

    return data_source_query, result_exists


def check_data_source_by_id(
        user: Person,
        data_source_id: UUID,
        require_ownership: bool = False,
        raise_http_errors: bool = False
):

    data_source_query, data_source_exists = query_data_sources(
        user=user,
        data_source_ids=[data_source_id],
        require_ownership=require_ownership,
        check_result_exists=True
    )

    data_source = data_source_query.exists()

    if raise_http_errors and not data_source_exists:
        raise HttpError(404, 'Data Source not found.')
    if raise_http_errors and data_source_exists and not data_source:
        raise HttpError(403, 'You do not have permission to perform this action on this Data Source.')

    return data_source


def get_data_source_by_id(
        user: Person,
        data_source_id: UUID,
        require_ownership: bool = False,
        raise_http_errors: bool = False
):

    data_source_query, data_source_exists = query_data_sources(
        user=user,
        data_source_ids=[data_source_id],
        require_ownership=require_ownership,
        check_result_exists=True
    )

    data_source = next(iter(data_source_query.all()), None)

    if raise_http_errors and not data_source_exists:
        raise HttpError(404, 'Data Source not found.')
    if raise_http_errors and data_source_exists and not data_source:
        raise HttpError(403, 'You do not have permission to perform this action on this Data Source.')

    return data_source


def build_data_source_response(data_source):
    return {
        'id': data_source.id,
        **{field: getattr(data_source, field) for field in DataSourceFields.__fields__.keys()},
    }
