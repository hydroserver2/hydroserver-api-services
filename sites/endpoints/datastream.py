from django.db import transaction
from django.http import JsonResponse
from ninja import Router, Schema

from sites.utils.authentication import thing_ownership_required, jwt_auth, jwt_check_user, datastream_ownership_required
from sites.models import Sensor, ObservedProperty, Unit, ProcessingLevel, Datastream, ThingAssociation
from sites.utils.datastream import datastream_to_dict, get_public_datastreams

router = Router()

class CreateDatastreamInput(Schema):
    thing_id: str
    method_id: str
    observed_property_id: str
    processing_level_id: str = None
    unit_id: str = None

    observation_type: str = None
    result_type: str = None
    status: str = None
    sampled_medium: str = None
    value_count: str = None
    no_data_value: str = None
    intended_time_spacing: str = None
    intended_time_spacing_units: str = None

    aggregation_statistic: str = None
    time_aggregation_interval: str = None
    time_aggregation_interval_units: str = None

    phenomenon_start_time: str = None
    phenomenon_end_time: str = None
    result_begin_time: str = None
    result_end_time: str = None


@router.post('/{thing_id}', auth=jwt_auth)
@thing_ownership_required
@transaction.atomic
def create_datastream(request, thing_id, data: CreateDatastreamInput):
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

    datastream = Datastream.objects.create(
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


class UpdateDatastreamInput(Schema):
    unit_id: str = None
    method_id: str = None
    observed_property_id: str = None
    processing_level_id: str = None

    observation_type: str = None
    result_type: str = None
    status: str = None
    sampled_medium: str = None
    value_count: str = None
    no_data_value: str = None
    intended_time_spacing: str = None
    intended_time_spacing_units: str = None

    aggregation_statistic: str = None
    time_aggregation_interval: str = None
    time_aggregation_interval_units: str = None

    phenomenon_start_time: str = None
    phenomenon_end_time: str = None
    result_begin_time: str = None
    result_end_time: str = None
    is_visible: bool = None

    data_source_id: str = None
    data_source_column: str = None


@router.patch('/patch/{datastream_id}', auth=jwt_auth)
@datastream_ownership_required
@transaction.atomic
def update_datastream(request, datastream_id: str, data: UpdateDatastreamInput):
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

    # if data.observation_type is not None:
    #     datastream.observation_type = data.observation_type
    # if data.result_type is not None:
    #     datastream.result_type = data.result_type
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
    if data.time_aggregation_interval_units is not None:
        try:
            datastream.time_aggregation_interval_units = Unit.objects.get(id=data.time_aggregation_interval_units)
        except Unit.DoesNotExist:
            return JsonResponse({'detail': 'time_aggregation_interval_units not found.'}, status=404)
    if data.phenomenon_start_time is not None:
        datastream.phenomenon_start_time = data.phenomenon_start_time
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
    if data.intended_time_spacing_units is not None:
        try:
            datastream.intended_time_spacing_units = Unit.objects.get(id=data.intended_time_spacing_units)
        except Unit.DoesNotExist:
            return JsonResponse({'detail': 'intended_time_spacing_units not found.'}, status=404)
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
