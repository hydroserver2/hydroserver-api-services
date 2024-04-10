import uuid
import copy
from ninja.errors import HttpError
from typing import List, Optional
from uuid import UUID
from django.db.models import Q
from django.db.models.query import QuerySet
from core.models import ObservedProperty
from accounts.models import Person
from .schemas import ObservedPropertyFields


def apply_observed_property_auth_rules(
        user: Optional[Person],
        observed_property_query: QuerySet,
        require_ownership: bool = False,
        require_ownership_or_unowned: bool = False,
        check_result: bool = False,
        raise_http_errors: bool = True
) -> (QuerySet, bool):

    result_exists = observed_property_query.exists() if check_result is True else None

    if not user and require_ownership is True:
        if raise_http_errors is True:
            raise HttpError(403, 'You are not authorized to access this Observed Property.')
        else:
            return observed_property_query.none(), result_exists

    if user and require_ownership is True:
        observed_property_query = observed_property_query.filter((Q(person=user) & Q(person__is_active=True)))
    elif user and require_ownership_or_unowned is True:
        observed_property_query = observed_property_query.filter(
            (Q(person=user) & Q(person__is_active=True)) | Q(person=None)
        )
    elif not user and require_ownership_or_unowned is True:
        observed_property_query = observed_property_query.filter(Q(person=None))

    return observed_property_query, result_exists


def query_observed_properties(
        user: Optional[Person],
        check_result_exists: bool = False,
        require_ownership: bool = False,
        require_ownership_or_unowned: bool = False,
        observed_property_ids: Optional[List[UUID]] = None,
        datastream_ids: Optional[List[UUID]] = None,
        raise_http_errors: Optional[bool] = True
):

    observed_property_query = ObservedProperty.objects

    if observed_property_ids:
        observed_property_query = observed_property_query.filter(id__in=observed_property_ids)

    if datastream_ids:
        observed_property_query = observed_property_query.filter(datastreams__id__in=datastream_ids)

    observed_property_query = observed_property_query.select_related('person', 'person__organization')

    observed_property_query, result_exists = apply_observed_property_auth_rules(
        user=user,
        observed_property_query=observed_property_query,
        require_ownership=require_ownership,
        require_ownership_or_unowned=require_ownership_or_unowned,
        check_result=check_result_exists,
        raise_http_errors=raise_http_errors
    )

    return observed_property_query, result_exists


def check_observed_property_by_id(
        user: Optional[Person],
        observed_property_id: UUID,
        require_ownership: bool = False,
        require_ownership_or_unowned: bool = False,
        raise_http_errors: bool = False
):

    observed_property_query, observed_property_exists = query_observed_properties(
        user=user,
        observed_property_ids=[observed_property_id],
        require_ownership=require_ownership,
        require_ownership_or_unowned=require_ownership_or_unowned,
        check_result_exists=True
    )

    observed_property = observed_property_query.exists()

    if raise_http_errors and not observed_property_exists:
        raise HttpError(404, 'Observed Property not found.')
    if raise_http_errors and observed_property_exists and not observed_property:
        raise HttpError(403, 'You do not have permission to perform this action on this Observed Property.')

    return observed_property


def get_observed_property_by_id(
        user: Optional[Person],
        observed_property_id: UUID,
        require_ownership: bool = False,
        require_ownership_or_unowned: bool = False,
        raise_http_errors: bool = False
):

    observed_property_query, observed_property_exists = query_observed_properties(
        user=user,
        observed_property_ids=[observed_property_id],
        require_ownership=require_ownership,
        require_ownership_or_unowned=require_ownership_or_unowned,
        check_result_exists=True
    )

    observed_property = next(iter(observed_property_query.all()), None)

    if raise_http_errors and not observed_property_exists:
        raise HttpError(404, 'Observed Property not found.')
    if raise_http_errors and observed_property_exists and not observed_property:
        raise HttpError(403, 'You do not have permission to perform this action on this Observed Property.')

    return observed_property


def build_observed_property_response(observed_property):
    return {
        'id': observed_property.id,
        'owner': observed_property.person.email if observed_property.person else None,
        **{field: getattr(observed_property, field) for field in ObservedPropertyFields.__fields__.keys()},
    }


def transfer_observed_property_ownership(datastream, new_owner, old_owner):

    if datastream.observed_property.person != old_owner or datastream.observed_property.person is None:
        return

    fields_to_compare = ['name', 'definition', 'description', 'type', 'code']
    same_properties = ObservedProperty.objects.filter(
        person=new_owner,
        **{f: getattr(datastream.observed_property, f) for f in fields_to_compare}
    )

    if same_properties.exists():
        datastream.observed_property = same_properties[0]
    else:
        new_property = copy.copy(datastream.observed_property)
        new_property.id = uuid.uuid4()
        new_property.person = new_owner
        new_property.save()
        datastream.observed_property = new_property

    datastream.save()
