from django.db import transaction
from django.http import JsonResponse
from ninja import Router, Schema
from pydantic import Field

from core.models import Sensor, ObservedProperty, Unit, ProcessingLevel, Datastream, ThingAssociation
from core.utils.authentication import thing_ownership_required, jwt_auth, jwt_check_user, datastream_ownership_required
from core.utils.datastream import datastream_to_dict, get_public_datastreams

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


class UpdateDatastreamFields(DatastreamFields):
    data_source_id: str = None
    data_source_column: str = None
    is_visible: bool = Field(None, alias='isVisible')


def update_object_from_data(obj, data_dict):
    for key, value in data_dict.items():
        if value is not None:
            setattr(obj, key, value)

fields_to_models = {
    'sensor': (Sensor, 'Sensor not found.'),
    'observed_property': (ObservedProperty, 'Observed Property not found.'),
    'unit': (Unit, 'Unit not found.'),
    'processing_level': (ProcessingLevel, 'Processing Level not found.'),
    'intended_time_spacing_units': (Unit, 'intended_time_spacing_units not found.'),
    'time_aggregation_interval_units': (Unit, 'time_aggregation_interval_units not found.')
}

non_FK_set = set(UpdateDatastreamFields.__fields__.keys()) - set(fields_to_models.keys())


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

    datastream_data = data.dict(include=non_FK_set)
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
def update_datastream(request, datastream_id: str, data: UpdateDatastreamFields):
    datastream = request.datastream
    
    for field, (model, error_message) in fields_to_models.items():
        field_value = getattr(data, field, None)
        if field_value is not None:
            try:
                setattr(datastream, field, model.objects.get(id=field_value))
            except model.DoesNotExist:
                return JsonResponse({'detail': error_message}, status=404)

    datastream_data = data.dict(include=non_FK_set)
    update_object_from_data(datastream, datastream_data)

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
