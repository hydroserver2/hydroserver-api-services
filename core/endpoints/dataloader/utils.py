from ninja.errors import HttpError
from typing import List, Optional
from uuid import UUID
from django.db.models import Q
from django.db.models.query import QuerySet
from core.models import Person, DataLoader
from .schemas import DataLoaderFields


def apply_data_loader_auth_rules(
        user: Person,
        data_loader_query: QuerySet,
        require_ownership: bool = False,
        check_result: bool = False
) -> (QuerySet, bool):

    result_exists = data_loader_query.exists() if check_result is True else None

    if not user and require_ownership is True:
        raise HttpError(403, 'You are not authorized to access this Data Loader.')

    if user and require_ownership is True:
        data_loader_query = data_loader_query.filter((Q(person=user) & Q(person__is_active=True)))

    return data_loader_query, result_exists


def query_data_loaders(
        user: Person,
        check_result_exists: bool = False,
        require_ownership: bool = False,
        data_loader_ids: Optional[List[UUID]] = None,
        datastream_ids: Optional[List[UUID]] = None
):

    data_loader_query = DataLoader.objects

    if data_loader_ids:
        data_loader_query = data_loader_query.filter(id__in=data_loader_ids)

    if datastream_ids:
        data_loader_query = data_loader_query.filter(datastreams__id__in=datastream_ids)

    data_loader_query, result_exists = apply_data_loader_auth_rules(
        user=user,
        data_loader_query=data_loader_query,
        require_ownership=require_ownership,
        check_result=check_result_exists
    )

    return data_loader_query, result_exists


def check_data_loader_by_id(
        user: Person,
        data_loader_id: UUID,
        require_ownership: bool = False,
        raise_http_errors: bool = False
):

    data_loader_query, data_loader_exists = query_data_loaders(
        user=user,
        data_loader_ids=[data_loader_id],
        require_ownership=require_ownership,
        check_result_exists=True
    )

    data_loader = data_loader_query.exists()

    if raise_http_errors and not data_loader_exists:
        raise HttpError(404, 'Data Loader not found.')
    if raise_http_errors and data_loader_exists and not data_loader:
        raise HttpError(403, 'You do not have permission to perform this action on this Data Loader.')

    return data_loader


def get_data_loader_by_id(
        user: Person,
        data_loader_id: UUID,
        require_ownership: bool = False,
        raise_http_errors: bool = False
):

    data_loader_query, data_loader_exists = query_data_loaders(
        user=user,
        data_loader_ids=[data_loader_id],
        require_ownership=require_ownership,
        check_result_exists=True
    )

    data_loader = next(iter(data_loader_query.all()), None)

    if raise_http_errors and not data_loader_exists:
        raise HttpError(404, 'Data Loader not found.')
    if raise_http_errors and data_loader_exists and not data_loader:
        raise HttpError(403, 'You do not have permission to perform this action on this Data Loader.')

    return data_loader


def build_data_loader_response(data_loader):
    return {
        'id': data_loader.id,
        **{field: getattr(data_loader, field) for field in DataLoaderFields.__fields__.keys()},
    }
