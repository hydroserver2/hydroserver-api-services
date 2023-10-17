import uuid
import copy
from ninja.errors import HttpError
from typing import List, Optional
from uuid import UUID
from django.db.models import Q
from django.db.models.query import QuerySet
from accounts.schemas import OrganizationFields, UserFields
from core.models import Person, Unit
from .schemas import UnitFields


def apply_unit_auth_rules(
        user: Person,
        unit_query: QuerySet,
        require_ownership: bool = False,
        require_ownership_or_unowned: bool = False,
        check_result: bool = False
) -> (QuerySet, bool):

    result_exists = unit_query.exists() if check_result is True else None

    if not user and require_ownership is True:
        raise HttpError(403, 'You are not authorized to access this Unit.')
    elif user and require_ownership_or_unowned is True:
        unit_query = unit_query.filter(Q(person=user) | Q(person=None))
    elif not user and require_ownership_or_unowned is True:
        unit_query = unit_query.filter(Q(person=None))

    if user and require_ownership is True:
        unit_query = unit_query.filter(Q(person=user))

    return unit_query, result_exists


def query_units(
        user: Person,
        check_result_exists: bool = False,
        require_ownership: bool = False,
        require_ownership_or_unowned: bool = False,
        unit_ids: Optional[List[UUID]] = None,
        datastream_ids: Optional[List[UUID]] = None
):

    unit_query = Unit.objects

    if unit_ids:
        unit_query = unit_query.filter(id__in=unit_ids)

    if datastream_ids:
        unit_query = unit_query.filter(datastreams__id__in=datastream_ids)

    unit_query = unit_query.select_related('person', 'person__organization')

    unit_query, result_exists = apply_unit_auth_rules(
        user=user,
        unit_query=unit_query,
        require_ownership=require_ownership,
        require_ownership_or_unowned=require_ownership_or_unowned,
        check_result=check_result_exists
    )

    return unit_query, result_exists


def check_unit_by_id(
        user: Person,
        unit_id: UUID,
        require_ownership: bool = False,
        require_ownership_or_unowned: bool = False,
        raise_http_errors: bool = False
):

    unit_query, unit_exists = query_units(
        user=user,
        unit_ids=[unit_id],
        require_ownership=require_ownership,
        require_ownership_or_unowned=require_ownership_or_unowned,
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
        require_ownership_or_unowned: bool = False,
        raise_http_errors: bool = False
):

    unit_query, unit_exists = query_units(
        user=user,
        unit_ids=[unit_id],
        require_ownership=require_ownership,
        require_ownership_or_unowned=require_ownership_or_unowned,
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
        'owner': {
            'organization': {
                **{field: getattr(unit.person.organization, field, None)
                   for field in OrganizationFields.__fields__.keys()}
            } if unit.person.organization else None,
            **{field: getattr(unit.person, field) for field in UserFields.__fields__.keys()}
        } if unit.person else None,
        **{field: getattr(unit, field) for field in UnitFields.__fields__.keys()},
    }


def transfer_unit_ownership(datastream, new_owner, old_owner):

    if datastream.unit.person != old_owner or datastream.unit.person is None:
        return

    fields_to_compare = ['name', 'symbol', 'definition', 'type']

    same_properties = Unit.objects.filter(
        person=new_owner,
        **{f: getattr(datastream.unit, f) for f in fields_to_compare}
    )

    if same_properties.exists():
        datastream.unit = same_properties[0]
    else:
        new_property = copy.copy(datastream.unit)
        new_property.id = uuid.uuid4()
        new_property.person = new_owner
        new_property.save()
        datastream.unit = new_property

    datastream.save()
