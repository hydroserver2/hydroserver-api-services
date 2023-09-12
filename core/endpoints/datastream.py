from django.db import transaction
from django.http import JsonResponse, StreamingHttpResponse
from ninja import Router, Schema
from pydantic import Field
from core.models import Sensor, ObservedProperty, Unit, ProcessingLevel, Datastream, ThingAssociation, Observation
from core.utils.authentication import thing_ownership_required, jwt_auth, jwt_check_user, datastream_ownership_required
from core.utils.datastream import datastream_to_dict, get_public_datastreams
from sensorthings.validators import allow_partial
from django.utils import timezone

router = Router(tags=['Datastreams'])


class DatastreamFields(Schema):
    # Foreign Keys
    # thing: str = Field(..., alias="thingId")
    sensor: str = Field(..., alias="sensorId")
    observed_property: str = Field(..., alias="observedPropertyId")
    processing_level: str = Field(..., alias="processingLevelId")
    unit: str = Field(..., alias="unitId")
    time_aggregation_interval_units: str = Field(..., alias="timeAggregationIntervalUnitsId")
    intended_time_spacing_units: str = Field(None, alias="intendedTimeSpacingUnitsId")

    name: str
    description: str
    observation_type: str = Field(..., alias="observationType")
    sampled_medium: str = Field(..., alias="sampledMedium")
    no_data_value: str = Field(..., alias="noDataValue")
    aggregation_statistic: str = Field(..., alias="aggregationStatistic")
    time_aggregation_interval: str = Field(..., alias="timeAggregationInterval")
    
    status: str = None
    result_type: str = Field(None, alias="resultType")
    value_count: str = Field(None, alias="valueCount")
    intended_time_spacing: str = Field(None, alias="intendedTimeSpacing")
    phenomenon_begin_time: str = Field(None, alias="phenomenonBeginTime")
    phenomenon_end_time: str = Field(None, alias="phenomenonEndTime")
    result_begin_time: str = Field(None, alias="resultBeginTime")
    result_end_time: str = Field(None, alias="resultEndTime")


@allow_partial
class DatastreamPatchBody(DatastreamFields):
    data_source_id: str = None
    data_source_column: str = None
    is_visible: bool = Field(None, alias='isVisible')


fields_to_models = {
    'sensor': (Sensor, 'Sensor not found.'),
    'observed_property': (ObservedProperty, 'Observed Property not found.'),
    'unit': (Unit, 'Unit not found.'),
    'processing_level': (ProcessingLevel, 'Processing Level not found.'),
    'intended_time_spacing_units': (Unit, 'intended_time_spacing_units not found.'),
    'time_aggregation_interval_units': (Unit, 'time_aggregation_interval_units not found.')
}

FK_set = set(fields_to_models.keys())
non_FK_set = set(DatastreamPatchBody.__fields__.keys()) - FK_set
non_FK_post_set = set(DatastreamFields.__fields__.keys()) - FK_set

@router.post('/{thing_id}', auth=jwt_auth)
@thing_ownership_required
@transaction.atomic
def create_datastream(request, thing_id, data: DatastreamFields):
    related_objects = {}
    
    for field, (model, error_message) in fields_to_models.items():
        field_value = getattr(data, field, None)
        if field_value:
            try:
                related_objects[field] = model.objects.get(id=field_value)
            except model.DoesNotExist:
                return JsonResponse({'detail': error_message}, status=404)

    datastream_data = data.dict(include=non_FK_post_set)
    datastream_data.update(related_objects)
    datastream_data.update({'thing': request.thing})

    datastream = Datastream.objects.create(**datastream_data)

    return JsonResponse(datastream_to_dict(datastream, request.thing_association))


@router.get('', auth=jwt_auth)
def get_datastreams(request):
    user_associations = ThingAssociation.objects.filter(
        person=request.authenticated_user,
        owns_thing=True
    ).prefetch_related('thing__datastreams')

    user_datastreams = [
        datastream_to_dict(datastream, association)
        for association in user_associations
        for datastream in association.thing.datastreams.all()
    ]

    return JsonResponse(user_datastreams, safe=False)


@router.get('/{thing_id}', auth=jwt_check_user)
def get_datastreams_for_thing(request, thing_id: str):
    if request.user_if_there_is_one:
        try:
            user_association = ThingAssociation.objects.get(
                person=request.user_if_there_is_one,
                thing_id=thing_id,
                owns_thing=True,
            )
        except ThingAssociation.DoesNotExist:
            return get_public_datastreams(thing_id=thing_id)
        return JsonResponse([
            datastream_to_dict(datastream, user_association)
            for datastream in user_association.thing.datastreams.all()
        ], safe=False)
    else:
        return get_public_datastreams(thing_id=thing_id)


@router.patch('/patch/{datastream_id}', auth=jwt_auth)
@datastream_ownership_required
@transaction.atomic
def update_datastream(request, datastream_id: str, data: DatastreamPatchBody):
    datastream = request.datastream

    foreign_data_dict = data.dict(include=FK_set, exclude_unset=True)
    for field, value in foreign_data_dict.items():
        model, error_message = fields_to_models.get(field)
        try:
            setattr(datastream, field, model.objects.get(id=value))
        except model.DoesNotExist:
            if field == 'intended_time_spacing_units':
                setattr(datastream, field, None)
                continue
            return JsonResponse({'detail': error_message}, status=404)

    datastream_data = data.dict(include=non_FK_set, exclude_unset=True)
    for key, value in datastream_data.items():
        setattr(datastream, key, value)

    datastream.save()

    return JsonResponse(datastream_to_dict(datastream, request.thing_association))


@router.delete('/{datastream_id}/temp')
@datastream_ownership_required
@transaction.atomic()
def delete_datastream(request, datastream_id: str):
    try:
        request.datastream.delete()
    except Exception as e:
        return JsonResponse(status=500, detail=str(e))

    return JsonResponse({'detail': 'Datastream deleted successfully.'}, status=200)


@router.get('/csv/{id}', auth=jwt_check_user)
def get_datastream_csv(request, id):
    # TODO: Prevent public access to private datastreams
    response = StreamingHttpResponse(generate_csv(id), content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="hello_world.csv"'
    return response


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


def generate_csv(id):
    datastream = Datastream.objects.select_related(
        'thing__location', 'sensor', 'observed_property', 'unit', 'processing_level'
    ).get(pk=id)

    thing = datastream.thing
    location = thing.location
    sensor = datastream.sensor
    observed_property = datastream.observed_property
    unit = datastream.unit
    processing_level = datastream.processing_level
    thing_association = ThingAssociation.objects.filter(thing=thing, is_primary_owner=True).first()
    primary_owner = thing_association.person if thing_association else None
    observations = Observation.objects.filter(datastream=datastream).order_by('phenomenon_time')
    
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
# IntendedTimeSpacingUnitsName: {datastream.intended_time_spacing_units.name if datastream.intended_time_spacing_units else None}
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

    yield "ResultTime,Result\n"

    for observation in observations:
        yield f"{observation.phenomenon_time.isoformat()},{observation.result}\n"