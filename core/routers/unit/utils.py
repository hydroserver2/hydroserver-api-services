from ninja.errors import HttpError
from typing import List, Optional
from uuid import UUID
from django.db.models import Q
from django.db.models.query import QuerySet
from core.models import Person, Unit
from .schemas import UnitFields


def apply_unit_auth_rules(
        user: Person,
        unit_query: QuerySet,
        require_ownership: bool = False,
        check_result: bool = False
) -> (QuerySet, bool):

    result_exists = unit_query.exists() if check_result is True else None

    if not user and require_ownership is True:
        raise HttpError(403, 'You are not authorized to access this Unit.')

    if user and require_ownership is True:
        unit_query = unit_query.filter(Q(person=user))

    return unit_query, result_exists


def query_units(
        user: Person,
        check_result_exists: bool = False,
        require_ownership: bool = False,
        unit_ids: Optional[List[UUID]] = None,
        datastream_ids: Optional[List[UUID]] = None
):

    unit_query = Unit.objects

    if unit_ids:
        unit_query = unit_query.filter(id__in=unit_ids)

    if datastream_ids:
        unit_query = unit_query.filter(datastreams__id__in=datastream_ids)

    unit_query, result_exists = apply_unit_auth_rules(
        user=user,
        unit_query=unit_query,
        require_ownership=require_ownership,
        check_result=check_result_exists
    )

    return unit_query, result_exists


def check_unit_by_id(
        user: Person,
        unit_id: UUID,
        require_ownership: bool = False,
        raise_http_errors: bool = False
):

    unit_query, unit_exists = query_units(
        user=user,
        unit_ids=[unit_id],
        require_ownership=require_ownership,
        check_result_exists=True
    )

    unit = unit_query.exists()

    if raise_http_errors and not unit_exists:
        raise HttpError(404, 'Unit not found.')
    if raise_http_errors and unit_exists and not unit:
        raise HttpError(403, 'You do not have permission to perform this action on this Unit.')

    return unit


def get_unit_by_id(
        user: Person,
        unit_id: UUID,
        require_ownership: bool = False,
        raise_http_errors: bool = False
):

    unit_query, unit_exists = query_units(
        user=user,
        unit_ids=[unit_id],
        require_ownership=require_ownership,
        check_result_exists=True
    )

    unit = next(iter(unit_query.all()), None)

    if raise_http_errors and not unit_exists:
        raise HttpError(404, 'Unit not found.')
    if raise_http_errors and unit_exists and not unit:
        raise HttpError(403, 'You do not have permission to perform this action on this Unit.')

    return unit


def build_unit_response(unit):
    return {
        'id': unit.id,
        **{field: getattr(unit, field) for field in UnitFields.__fields__.keys()},
    }
