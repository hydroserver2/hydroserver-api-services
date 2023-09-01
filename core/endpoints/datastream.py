from django.db import transaction
from django.http import JsonResponse
from ninja import Router, Schema
from pydantic import Field

from core.utils.authentication import thing_ownership_required, jwt_auth, jwt_check_user, datastream_ownership_required
from core.models import Sensor, ObservedProperty, Unit, ProcessingLevel, Datastream, ThingAssociation
from core.utils.datastream import datastream_to_dict, get_public_datastreams

router = Router(tags=['Datastreams'])


class DatastreamFields(Schema):
    name: str
    description: str
    thing_id: str = Field(..., alias="thingId")
    method_id: str = Field(..., alias="methodId")
    observed_property_id: str = Field(..., alias="observedPropertyId")
    processing_level_id: str = Field(..., alias="processingLevelId")
    unit_id: str = Field(..., alias="unitId")

    observation_type: str = Field(..., alias="observationType")
    result_type: str = Field(None, alias="resultType")
    status: str = None
    sampled_medium: str = Field(..., alias="sampledMedium")
    value_count: str = Field(None, alias="valueCount")
    no_data_value: str = Field(..., alias="noDataValue")
    aggregation_statistic: str = Field(..., alias="aggregationStatistic")

    intended_time_spacing: str = Field(None, alias="intendedTimeSpacing")
    intended_time_spacing_units_id: str = Field(None, alias="intendedTimeSpacingUnitsId")
    time_aggregation_interval: str = Field(..., alias="timeAggregationInterval")
    time_aggregation_interval_units_id: str = Field(..., alias="timeAggregationIntervalUnitsId")

    phenomenon_begin_time: str = Field(None, alias="phenomenonBeginTime")
    phenomenon_end_time: str = Field(None, alias="phenomenonEndTime")
    result_begin_time: str = Field(None, alias="resultBeginTime")
    result_end_time: str = Field(None, alias="resultEndTime")



@router.post('/{thing_id}', auth=jwt_auth)
@thing_ownership_required
@transaction.atomic
def create_datastream(request, thing_id, data: DatastreamFields):
    try:
        sensor = Sensor.objects.get(id=data.method_id)
    except Sensor.DoesNotExist:
        return JsonResponse({'detail': 'Sensor not found.'}, status=404)

    try:
        observed_property = ObservedProperty.objects.get(id=data.observed_property_id)
    except ObservedProperty.DoesNotExist:
        return JsonResponse({'detail': 'Observed Property not found.'}, status=404)

    try:
        unit = Unit.objects.get(id=data.unit_id) if data.unit_id else None
    except Unit.DoesNotExist:
        return JsonResponse({'detail': 'Unit not found.'}, status=404)

    if data.processing_level_id:
        processing_level = ProcessingLevel.objects.get(id=data.processing_level_id)
    else:
        processing_level = None

    try:
        intended_time_spacing_units = Unit.objects.get(id=data.intended_time_spacing_units_id) if data.intended_time_spacing_units_id else None
    except Unit.DoesNotExist:
        return JsonResponse({'detail': 'intended_time_spacing_units not found.'}, status=404)
    
    try:
        time_aggregation_interval_units = Unit.objects.get(id=data.time_aggregation_interval_units_id)
    except Unit.DoesNotExist:
        return JsonResponse({'detail': 'time_aggregation_interval_units not found.'}, status=404)

    datastream = Datastream.objects.create(
        name="Site Datastream",
        description="Site Datastream",
        observed_property=observed_property,
        unit=unit,
        processing_level=processing_level,
        sampled_medium=data.sampled_medium,
        status=data.status,
        no_data_value=float(data.no_data_value) if data.no_data_value else None,
        aggregation_statistic=data.aggregation_statistic,
        result_type='Time Series Coverage',
        observation_type='OM_Measurement',
        thing=request.thing,
        sensor=sensor,
        intended_time_spacing_units=intended_time_spacing_units,
        time_aggregation_interval_units=time_aggregation_interval_units,
        time_aggregation_interval=data.time_aggregation_interval,
        intended_time_spacing = data.intended_time_spacing if data.intended_time_spacing else None,
    )

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


class UpdateDatastreamFields(DatastreamFields):
    data_source_id: str = None
    data_source_column: str = None
    is_visible: bool = Field(None, alias='isVisible')


@router.patch('/patch/{datastream_id}', auth=jwt_auth)
@datastream_ownership_required
@transaction.atomic
def update_datastream(request, datastream_id: str, data: UpdateDatastreamFields):
    datastream = request.datastream
    
    if data.method_id is not None:
        try:
            datastream.sensor = Sensor.objects.get(id=data.method_id)
        except Sensor.DoesNotExist:
            return JsonResponse({'detail': 'Sensor not found.'}, status=404)

    if data.observed_property_id is not None:
        try:
            datastream.observed_property = ObservedProperty.objects.get(id=data.observed_property_id)
        except ObservedProperty.DoesNotExist:
            return JsonResponse({'detail': 'Observed Property not found.'}, status=404)

    if data.unit_id is not None:
        try:
            datastream.unit = Unit.objects.get(id=data.unit_id)
        except Unit.DoesNotExist:
            return JsonResponse({'detail': 'Unit not found.'}, status=404)

    if data.processing_level_id is not None:
        try:
            datastream.processing_level = ProcessingLevel.objects.get(id=data.processing_level_id)
        except ProcessingLevel.DoesNotExist:
            return JsonResponse({'detail': 'Processing Level not found.'}, status=404)

    if data.intended_time_spacing_units_id is not None:
        try:
            datastream.intended_time_spacing_units = Unit.objects.get(id=data.intended_time_spacing_units_id)
        except Unit.DoesNotExist:
            return JsonResponse({'detail': 'intended_time_spacing_units not found.'}, status=404)
        
    if data.time_aggregation_interval_units_id is not None:
        try:
            datastream.time_aggregation_interval_units = Unit.objects.get(id=data.time_aggregation_interval_units_id)
        except Unit.DoesNotExist:
            return JsonResponse({'detail': 'time_aggregation_interval_units not found.'}, status=404)
        
    if data.observation_type is not None:
        datastream.observation_type = data.observation_type
    if data.result_type is not None:
        datastream.result_type = data.result_type
    if data.status is not None:
        datastream.status = data.status
    if data.sampled_medium is not None:
        datastream.sampled_medium = data.sampled_medium
    if data.no_data_value is not None:
        datastream.no_data_value = float(data.no_data_value) if data.no_data_value else None
    if data.aggregation_statistic is not None:
        datastream.aggregation_statistic = data.aggregation_statistic
    if data.time_aggregation_interval is not None:
        datastream.time_aggregation_interval = data.time_aggregation_interval
    if data.phenomenon_begin_time is not None:
        datastream.phenomenon_begin_time = data.phenomenon_begin_time
    if data.phenomenon_end_time is not None:
        datastream.phenomenon_end_time = data.phenomenon_end_time
    if data.result_begin_time is not None:
        datastream.result_begin_time = data.result_begin_time
    if data.result_end_time is not None:
        datastream.result_end_time = data.result_end_time
    if data.value_count is not None:
        datastream.value_count = data.value_count
    if data.intended_time_spacing is not None:
        datastream.intended_time_spacing = data.intended_time_spacing
    if data.is_visible is not None:
        datastream.is_visible = data.is_visible

    if hasattr(data, 'data_source_id') is not None:
        datastream.data_source_id = data.data_source_id
    if hasattr(data, 'column') is not None:
        datastream.data_source_column = data.data_source_column

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
