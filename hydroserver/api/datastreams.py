from hydroserver.api.api import api
from django.db import transaction
from django.http import JsonResponse
from hydroserver.api.util import datastream_ownership_required, datastream_to_dict, get_public_datastreams, \
   jwt_auth, jwt_check_user, thing_ownership_required
from hydroserver.schemas import CreateDatastreamInput, UpdateDatastreamInput
# from hydroserver.schemas import *
from sites.models import Datastream, Sensor, ObservedProperty, Unit, ThingAssociation, ProcessingLevel


@api.post('/datastreams/{thing_id}', auth=jwt_auth)
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
        result_type=data.result_type if data.result_type else 'Time Series Coverage',
        observation_type=data.observation_type if data.observation_type else 'OM_Measurement',
        thing=request.thing,
        sensor=sensor,
    )

    return JsonResponse(datastream_to_dict(datastream, request.thing_association))


@api.get('/datastreams', auth=jwt_auth)
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


@api.get('/datastreams/{thing_id}', auth=jwt_check_user)
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



@api.patch('/datastreams/patch/{datastream_id}', auth=jwt_auth)
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

    if data.observation_type is not None:
        datastream.observation_type = data.observation_type
    if data.result_type is not None:
        datastream.result_type = data.result_type
    if data.status is not None:
        datastream.status = data.status
    if data.sampled_medium is not None:
        datastream.sampled_medium = data.sampled_medium
    if data.no_data_value is not None:
        datastream.no_data_value = data.no_data_value
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

    datastream.save()

    return JsonResponse(datastream_to_dict(datastream, request.thing_association))


@api.delete('/datastreams/{datastream_id}/temp')
@datastream_ownership_required
@transaction.atomic()
def delete_datastream(request, datastream_id: str):
    try:
        request.datastream.delete()
    except Exception as e:
        return JsonResponse(status=500, detail=str(e))

    return JsonResponse({'detail': 'Datastream deleted successfully.'}, status=200)