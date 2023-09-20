from ninja.errors import HttpError
from typing import List, Optional
from uuid import UUID
from django.db.models import Q
from django.db.models.query import QuerySet
from core.models import Person, ObservedProperty
from .schemas import ObservedPropertyFields


def apply_observed_property_auth_rules(
        user: Person,
        observed_property_query: QuerySet,
        require_ownership: bool = False,
        check_result: bool = False
) -> (QuerySet, bool):

    result_exists = observed_property_query.exists() if check_result is True else None

    if not user and require_ownership is True:
        raise HttpError(403, 'You are not authorized to access this Observed Property.')

    if user and require_ownership is True:
        observed_property_query = observed_property_query.filter(Q(person=user))

    return observed_property_query, result_exists


def query_observed_properties(
        user: Person,
        check_result_exists: bool = False,
        require_ownership: bool = False,
        observed_property_ids: Optional[List[UUID]] = None,
        datastream_ids: Optional[List[UUID]] = None
):

    observed_property_query = ObservedProperty.objects

    if observed_property_ids:
        observed_property_query = observed_property_query.filter(id__in=observed_property_ids)

    if datastream_ids:
        observed_property_query = observed_property_query.filter(datastreams__id__in=datastream_ids)

    observed_property_query, result_exists = apply_observed_property_auth_rules(
        user=user,
        observed_property_query=observed_property_query,
        require_ownership=require_ownership,
        check_result=check_result_exists
    )

    return observed_property_query, result_exists


def check_observed_property_by_id(
        user: Person,
        observed_property_id: UUID,
        require_ownership: bool = False,
        raise_http_errors: bool = False
):

    observed_property_query, observed_property_exists = query_observed_properties(
        user=user,
        observed_property_ids=[observed_property_id],
        require_ownership=require_ownership,
        check_result_exists=True
    )

    observed_property = observed_property_query.exists()

    if raise_http_errors and not observed_property_exists:
        raise HttpError(404, 'Observed Property not found.')
    if raise_http_errors and observed_property_exists and not observed_property:
        raise HttpError(403, 'You do not have permission to perform this action on this Observed Property.')

    return observed_property


def get_observed_property_by_id(
        user: Person,
        observed_property_id: UUID,
        require_ownership: bool = False,
        raise_http_errors: bool = False
):

    observed_property_query, observed_property_exists = query_observed_properties(
        user=user,
        observed_property_ids=[observed_property_id],
        require_ownership=require_ownership,
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
        **{field: getattr(observed_property, field) for field in ObservedPropertyFields.__fields__.keys()},
    }
