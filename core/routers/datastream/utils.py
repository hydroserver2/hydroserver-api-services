import operator
from ninja.errors import HttpError
from django.db.models import Q, Count
from django.db.models.query import QuerySet
from uuid import UUID
from typing import List, Optional
from functools import reduce
from core.models import Person, Datastream
from core.routers.sensor.utils import check_sensor_by_id
from core.routers.observedproperty.utils import check_observed_property_by_id
from core.routers.processinglevel.utils import check_processing_level_by_id
from core.routers.unit.utils import check_unit_by_id
from .schemas import DatastreamFields


def apply_datastream_auth_rules(
        user: Person,
        datastream_query: QuerySet,
        require_ownership: bool = False,
        require_primary_ownership: bool = False,
        require_unaffiliated: bool = False,
        check_result: bool = False
) -> (QuerySet, bool):

    if not user and (require_ownership or require_unaffiliated or require_primary_ownership):
        raise HttpError(403, 'You do not have permission to perform this action on this Datastream.')

    result_exists = datastream_query.exists() if check_result is True else None

    auth_filters = []

    if user:
        auth_filters.append((
            Q(thing__is_private=False) | (Q(thing__associates__person=user) & Q(thing__associates__owns_thing=True))
        ))
    else:
        auth_filters.append(Q(thing__is_private=False))

    if require_ownership:
        auth_filters.append(Q(thing__associates__person=user) & Q(thing__associates__owns_thing=True))

    if require_primary_ownership:
        auth_filters.append(Q(thing__associates__person=user) & Q(thing__associates__is_primary_owner=True))

    if require_unaffiliated:
        auth_filters.append(Q(thing__associates__person=user) & Q(thing__associates__owns_thing=False))

    datastream_query = datastream_query.annotate(
        associates_count=Count('thing__associates', filter=reduce(operator.and_, auth_filters))
    ).filter(
        associates_count__gt=0
    )

    return datastream_query, result_exists


def query_datastreams(
        user: Person,
        check_result_exists: bool = False,
        require_ownership: bool = False,
        require_primary_ownership: bool = False,
        require_unaffiliated: bool = False,
        datastream_ids: Optional[List[UUID]] = None,
        thing_ids: Optional[List[UUID]] = None,
        sensor_ids: Optional[List[UUID]] = None,
        observed_property_ids: Optional[List[UUID]] = None
) -> (QuerySet, bool):

    datastream_query = Datastream.objects

    if datastream_ids:
        datastream_query = datastream_query.filter(id__in=datastream_ids)

    if thing_ids:
        datastream_query = datastream_query.filter(thing_id__in=thing_ids)

    if sensor_ids:
        datastream_query = datastream_query.filter(sensor_id__in=sensor_ids)

    if observed_property_ids:
        datastream_query = datastream_query.filter(observed_property_id__in=observed_property_ids)

    datastream_query = datastream_query.select_related(
        'processing_level', 'unit', 'intended_time_spacing_units', 'time_aggregation_interval_units'
    )

    datastream_query, result_exists = apply_datastream_auth_rules(
        user=user,
        datastream_query=datastream_query,
        require_ownership=require_ownership,
        require_primary_ownership=require_primary_ownership,
        require_unaffiliated=require_unaffiliated,
        check_result=check_result_exists
    )

    return datastream_query, result_exists


def check_datastream_by_id(
        user: Person,
        datastream_id: UUID,
        require_ownership: bool = False,
        require_primary_ownership: bool = False,
        require_unaffiliated: bool = False,
        raise_http_errors: bool = False
) -> bool:

    datastream_query, datastream_exists = query_datastreams(
        user=user,
        datastream_ids=[datastream_id],
        require_ownership=require_ownership,
        require_primary_ownership=require_primary_ownership,
        require_unaffiliated=require_unaffiliated,
        check_result_exists=True
    )

    datastream = datastream_query.exists()

    if raise_http_errors and not datastream_exists:
        raise HttpError(404, 'Datastream not found.')
    if raise_http_errors and datastream_exists and not datastream:
        raise HttpError(403, 'You do not have permission to perform this action on this Datastream.')

    return datastream


def get_datastream_by_id(
        user: Person,
        datastream_id: UUID,
        require_ownership: bool = False,
        require_primary_ownership: bool = False,
        require_unaffiliated: bool = False,
        raise_http_errors: bool = True
):

    datastream_query, datastream_exists = query_datastreams(
        user=user,
        datastream_ids=[datastream_id],
        require_ownership=require_ownership,
        require_primary_ownership=require_primary_ownership,
        require_unaffiliated=require_unaffiliated,
        check_result_exists=True
    )

    datastream = next(iter(datastream_query.all()), None)

    if raise_http_errors and not datastream_exists:
        raise HttpError(404, 'Datastream not found.')
    if raise_http_errors and datastream_exists and not datastream:
        raise HttpError(403, 'You do not have permission to perform this action on this Datastream.')

    return datastream


def build_datastream_response(datastream):

    return {
        'id': datastream.id,
        'thing_id': datastream.thing_id,
        **{field: getattr(datastream, field) for field in DatastreamFields.__fields__.keys()},
    }


def check_related_fields(user, data):

    if data.sensor_id:
        check_sensor_by_id(
            user=user,
            sensor_id=data.sensor_id,
            require_ownership=True,
            raise_http_errors=True
        )

    if data.observed_property_id:
        check_observed_property_by_id(
            user=user,
            observed_property_id=data.observed_property_id,
            require_ownership=True,
            raise_http_errors=True
        )

    if data.processing_level_id:
        check_processing_level_by_id(
            user=user,
            processing_level_id=data.processing_level_id,
            require_ownership=True,
            raise_http_errors=True
        )

    if data.unit_id:
        check_unit_by_id(
            user=user,
            unit_id=data.unit_id,
            require_ownership=True,
            raise_http_errors=True
        )

    if data.time_aggregation_interval_units_id:
        check_unit_by_id(
            user=user,
            unit_id=data.time_aggregation_interval_units_id,
            require_ownership=True,
            raise_http_errors=True
        )

    if data.intended_time_spacing_units_id:
        check_unit_by_id(
            user=user,
            unit_id=data.intended_time_spacing_units_id,
            require_ownership=True,
            raise_http_errors=True
        )
