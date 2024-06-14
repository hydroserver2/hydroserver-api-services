import pandas as pd
from collections import defaultdict
from django.utils import timezone
from django.http import StreamingHttpResponse


def export_csv(request, thing_pk):
    """
    This algorithm exports all the observations associated with the passed in thing_pk into a CSV file in O(n) time.
    The use of select_related() improves the efficiency of the algorithm by reducing the number of database queries.
    This iterates over the observations once, storing the observations in a dictionary, then yields the rows one by one.
    This algorithm is memory-efficient since it doesn't load the whole data into memory.
    """
    from core.models import Thing, Observation

    thing = Thing.objects.get(id=thing_pk)
    response = StreamingHttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(thing.name)

    observations = Observation.objects.filter(datastream__thing_id=thing_pk).select_related(
        'datastream__observed_property')

    def csv_iter():
        observed_property_names = list(
            observations.values_list('datastream__observed_property__name', flat=True).distinct())
        yield f'DateTime,{",".join(observed_property_names)}\n'

        # Group observations by result_time and yield row by row
        observations_by_time = defaultdict(lambda: {name: '' for name in observed_property_names})
        for obs in observations:
            observations_by_time[obs.phenomenon_time][obs.datastream.observed_property.name] = obs.result

        for result_time, props in observations_by_time.items():
            yield f'{result_time.strftime("%m/%d/%Y %I:%M:%S %p")},' + ','.join(props.values()) + '\n'

    response.streaming_content = csv_iter()
    return response


def process_csv_file(file_path, sensor):
    from core.models import Observation

    metadata = pd.read_csv(file_path, nrows=1, header=None).values.tolist()[0]
    df = pd.read_csv(file_path, header=1,
                     usecols=[datastream.observed_property.name for datastream in sensor.datastreams.all() if
                              datastream.observed_property] + ["TIMESTAMP"])
    units = df.iloc[0]
    measurement_type = df.iloc[1]
    df = df.drop([0, 1])

    time_series = df.iloc[:, 0]

    observations = []
    for datastream in sensor.datastreams.all():
        column_name = datastream.observed_property.name
        if column_name not in df.columns:
            continue
        data = df[column_name]

        for j, time in enumerate(time_series):
            observations.append(Observation(phenomenon_time=time, result=data[j], datastream=datastream))

        Observation.objects.bulk_create(observations)


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
    from core.models import ThingAssociation, ResultQualifier, Observation

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
# TimeAggregationIntervalUnitsName: {datastream.time_aggregation_interval_units}
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
        result_qualifiers_str = ','.join(qualifier_code_map.get(uuid, "")
                                         for uuid in (observation.result_qualifiers or []))
        if result_qualifiers_str:
            yield f'{observation.phenomenon_time.isoformat()},{observation.result},"{result_qualifiers_str}"\n'
        else:
            yield f'{observation.phenomenon_time.isoformat()},{observation.result},\n'
