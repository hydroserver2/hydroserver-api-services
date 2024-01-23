import operator
from ninja.errors import HttpError
from django.db.models import Q, Count
from django.db.models.query import QuerySet
from django.utils import timezone
from uuid import UUID
from typing import List, Optional
from datetime import datetime
from functools import reduce
from core.models import Person, Datastream, ThingAssociation, Observation, ResultQualifier
from core.endpoints.thing.utils import check_thing_by_id
from core.endpoints.sensor.utils import check_sensor_by_id
from core.endpoints.observedproperty.utils import check_observed_property_by_id
from core.endpoints.processinglevel.utils import check_processing_level_by_id
from core.endpoints.unit.utils import check_unit_by_id
from .schemas import DatastreamFields


def apply_datastream_auth_rules(
        user: Optional[Person],
        datastream_query: QuerySet,
        require_ownership: bool = False,
        require_primary_ownership: bool = False,
        require_unaffiliated: bool = False,
        ignore_privacy: bool = False,
        check_result: bool = False,
        raise_http_errors: bool = True
) -> (QuerySet, bool):

    result_exists = datastream_query.exists() if check_result is True else None

    if not user and (require_ownership or require_unaffiliated or require_primary_ownership):
        if raise_http_errors is True:
            raise HttpError(403, 'You do not have permission to perform this action on this Datastream.')
        else:
            return datastream_query.none(), result_exists

    auth_filters = [
        ~(Q(thing__associates__is_primary_owner=True) &
          Q(thing__associates__person__is_active=False))
    ]

    if ignore_privacy is False:
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
        associates_count=Count(
            'thing__associates', filter=reduce(operator.and_, auth_filters) if auth_filters else None
        )
    ).filter(
        associates_count__gt=0
    )

    return datastream_query, result_exists


def apply_recent_datastream_filter(
        datastream_query: QuerySet,
        modified_since: datetime
) -> QuerySet:

    datastream_history_filter = Q(log__history_date__gt=modified_since)

    datastream_query = datastream_query.filter(
        datastream_history_filter
    )

    return datastream_query


def query_datastreams(
        user: Optional[Person],
        check_result_exists: bool = False,
        require_ownership: bool = False,
        require_primary_ownership: bool = False,
        require_unaffiliated: bool = False,
        ignore_privacy: bool = False,
        datastream_ids: Optional[List[UUID]] = None,
        thing_ids: Optional[List[UUID]] = None,
        sensor_ids: Optional[List[UUID]] = None,
        data_source_ids: Optional[List[UUID]] = None,
        observed_property_ids: Optional[List[UUID]] = None,
        modified_since: Optional[datetime] = None,
        raise_http_errors: Optional[bool] = True
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

    if data_source_ids:
        datastream_query = datastream_query.filter(data_source_id__in=data_source_ids)

    datastream_query = datastream_query.select_related('processing_level', 'unit', 'time_aggregation_interval_units')

    if modified_since:
        datastream_query = datastream_query.prefetch_related('log')
        datastream_query = apply_recent_datastream_filter(datastream_query, modified_since)

    datastream_query, result_exists = apply_datastream_auth_rules(
        user=user,
        datastream_query=datastream_query,
        require_ownership=require_ownership,
        require_primary_ownership=require_primary_ownership,
        require_unaffiliated=require_unaffiliated,
        ignore_privacy=ignore_privacy,
        check_result=check_result_exists,
        raise_http_errors=raise_http_errors
    )

    return datastream_query, result_exists


def check_datastream_by_id(
        user: Optional[Person],
        datastream_id: UUID,
        require_ownership: bool = False,
        require_primary_ownership: bool = False,
        require_unaffiliated: bool = False,
        ignore_privacy: bool = False,
        raise_http_errors: bool = False
) -> bool:

    datastream_query, datastream_exists = query_datastreams(
        user=user,
        datastream_ids=[datastream_id],
        require_ownership=require_ownership,
        require_primary_ownership=require_primary_ownership,
        require_unaffiliated=require_unaffiliated,
        ignore_privacy=ignore_privacy,
        check_result_exists=True
    )

    datastream = datastream_query.exists()

    if raise_http_errors and not datastream_exists:
        raise HttpError(404, 'Datastream not found.')
    if raise_http_errors and datastream_exists and not datastream:
        raise HttpError(403, 'You do not have permission to perform this action on this Datastream.')

    return datastream


def get_datastream_by_id(
        user: Optional[Person],
        datastream_id: UUID,
        require_ownership: bool = False,
        require_primary_ownership: bool = False,
        require_unaffiliated: bool = False,
        ignore_privacy: bool = False,
        raise_http_errors: bool = True
):

    datastream_query, datastream_exists = query_datastreams(
        user=user,
        datastream_ids=[datastream_id],
        require_ownership=require_ownership,
        require_primary_ownership=require_primary_ownership,
        require_unaffiliated=require_unaffiliated,
        ignore_privacy=ignore_privacy,
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


def check_related_fields(user, metadata):

    if metadata.thing_id:
        check_thing_by_id(
            user=user,
            thing_id=metadata.thing_id,
            require_ownership=True,
            raise_http_errors=True
        )

    if metadata.sensor_id:
        check_sensor_by_id(
            user=user,
            sensor_id=metadata.sensor_id,
            require_ownership_or_unowned=True,
            raise_http_errors=True
        )

    if metadata.observed_property_id:
        check_observed_property_by_id(
            user=user,
            observed_property_id=metadata.observed_property_id,
            require_ownership_or_unowned=True,
            raise_http_errors=True
        )

    if metadata.processing_level_id:
        check_processing_level_by_id(
            user=user,
            processing_level_id=metadata.processing_level_id,
            require_ownership_or_unowned=True,
            raise_http_errors=True
        )

    if metadata.unit_id:
        check_unit_by_id(
            user=user,
            unit_id=metadata.unit_id,
            require_ownership_or_unowned=True,
            raise_http_errors=True
        )

    if metadata.time_aggregation_interval_units_id:
        check_unit_by_id(
            user=user,
            unit_id=metadata.time_aggregation_interval_units_id,
            require_ownership_or_unowned=True,
            raise_http_errors=True
        )


def get_organization_info(owner):
    if not owner.organization:
        return '# Organization: None'

    organization = owner.organization
    return f'''# OrganizationCode: {organization.code}
# OrganizationName: {organization.name}
# OrganizationDescription: {organization.description}
# OrganizationType: {organization.type}
# OrganizationLink: {organization.link}'''


def get_site_owner_info(primary_owner):
    if not primary_owner:
        return "# Site Owner Information: None"

    return f"""# Site Owner Information:
# -------------------------------------
# Name: {primary_owner.first_name} {primary_owner.last_name}
# Phone: {primary_owner.phone}
# Email: {primary_owner.email}
# Address: {primary_owner.address}
# PersonLink: {primary_owner.link}
{get_organization_info(primary_owner)}"""


def generate_csv(datastream):

    thing = datastream.thing
    location = thing.location
    sensor = datastream.sensor
    observed_property = datastream.observed_property
    unit = datastream.unit
    processing_level = datastream.processing_level
    thing_association = ThingAssociation.objects.filter(thing=thing, is_primary_owner=True).first()
    primary_owner = thing_association.person if thing_association else None
    observations = (Observation.objects.filter(datastream_id=datastream.id)
                    .only('phenomenon_time', 'result', 'result_qualifiers')
                    .order_by('phenomenon_time'))

    latitude = round(location.latitude, 6) if location.latitude else "None"
    longitude = round(location.longitude, 6) if location.longitude else "None"
    elevation_m = round(location.elevation_m, 6) if location.elevation_m else "None"

    yield f'''# =============================================================================
# Generated on: {timezone.now().isoformat()}
# 
{get_site_owner_info(primary_owner)}
#
# Site Information:
# -------------------------------------
# Name: {thing.name}
# Description: {thing.description}
# SamplingFeatureType: {thing.sampling_feature_type}
# SamplingFeatureCode: {thing.sampling_feature_code}
# SiteType: {thing.site_type}
#
# Location Information:
# -------------------------------------
# Name: {location.name}
# Description: {location.description}
# Latitude: {latitude}
# Longitude: {longitude}
# Elevation_m: {elevation_m}
# ElevationDatum: {location.elevation_datum}
# State: {location.state}
# County: {location.county}
#
# Datastream Information:
# -------------------------------------
# Name: {datastream.name}
# Description: {datastream.description}
# ObservationType: {datastream.observation_type}
# ResultType: {datastream.result_type}
# Status: {datastream.status}
# SampledMedium: {datastream.sampled_medium}
# ValueCount: {datastream.value_count}
# NoDataValue: {datastream.no_data_value}
# IntendedTimeSpacing: {datastream.intended_time_spacing}
# IntendedTimeSpacingUnits: {datastream.intended_time_spacing_units}
# AggregationStatistic: {datastream.aggregation_statistic}
# TimeAggregationInterval: {datastream.time_aggregation_interval}
# TimeAggregationIntervalUnitsName: {datastream.time_aggregation_interval_units.name}
#
# Method Information:
# -------------------------------------
# Name: {sensor.name}
# Description: {sensor.description}
# MethodCode: {sensor.method_code}
# MethodType: {sensor.method_type}
# MethodLink: {sensor.method_link}
# SensorManufacturerName: {sensor.manufacturer}
# SensorModelName: {sensor.model}
# SensorModelLink: {sensor.model_link}
#
# Observed Property Information:
# -------------------------------------
# Name: {observed_property.name}
# Definition: {observed_property.definition}
# Description: {observed_property.description}
# VariableType: {observed_property.type}
# VariableCode: {observed_property.code}
#
# Unit Information:
# -------------------------------------
# Name: {unit.name}
# Symbol: {unit.symbol}
# Definition: {unit.definition}
# UnitType: {unit.type}
#
# Processing Level Information:
# -------------------------------------
# Code: {processing_level.code}
# Definition: {processing_level.definition}
# Explanation: {processing_level.explanation}
#
# Data Disclaimer:
# -------------------------------------
# Output date/time values are in UTC unless they were input to HydroServer without time zone offset information. In that case, date/time values are output as they were supplied to HydroServer.
# {thing.data_disclaimer if thing.data_disclaimer else ""}
# =============================================================================
'''

    yield "ResultTime,Result,ResultQualifiers\n"

    qualifiers = ResultQualifier.objects.filter(person=primary_owner)
    qualifier_code_map = {qualifier.id: qualifier.code for qualifier in qualifiers}

    for observation in observations:
        result_qualifiers_str = ','.join(qualifier_code_map.get(uuid, "") for uuid in (observation.result_qualifiers or []))
        if result_qualifiers_str:
            yield f'{observation.phenomenon_time.isoformat()},{observation.result},"{result_qualifiers_str}"\n'
        else:
            yield f'{observation.phenomenon_time.isoformat()},{observation.result},\n'

