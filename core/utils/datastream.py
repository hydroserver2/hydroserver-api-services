from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from core.models import Observation, Thing
import math


def datastream_to_dict(datastream, association=None, add_recent_observations=True):
    observation_list = []
    most_recent_observation = None
    is_stale = True
    if add_recent_observations:
        if hasattr(datastream, 'phenomenon_end_time') and datastream.phenomenon_end_time is not None:
            if datastream.phenomenon_end_time > timezone.now() - timedelta(hours=72):
                is_stale = False
            since_time = datastream.phenomenon_end_time - timedelta(hours=72)
            observations = Observation.objects.filter(
                datastream=datastream, phenomenon_time__gte=since_time
            ).order_by('-phenomenon_time')
            for observation in observations:
                observation_list.append({
                    "id": observation.id,
                    "result": observation.result if not math.isnan(observation.result) else None,
                    "phenomenonTime": observation.phenomenon_time,
                })
            if observation_list:
                most_recent_observation = observation_list[0]

    return {
        "id": datastream.pk,
        "name": datastream.name,
        "description": datastream.description,
        "thingId": datastream.thing.id,
        "observationType": datastream.observation_type,
        "resultType": datastream.result_type,
        "status": datastream.status,
        "sampledMedium": datastream.sampled_medium,
        "noDataValue": datastream.no_data_value,
        "aggregationStatistic": datastream.aggregation_statistic,
        "observations": observation_list if observation_list else None,
        "mostRecentObservation": most_recent_observation,

        "unitId": datastream.unit.pk if datastream.unit else None,
        "observedPropertyId": datastream.observed_property.pk if datastream.observed_property else None,
        "sensorId": datastream.sensor.pk if datastream.sensor else None,
        "processingLevelId": datastream.processing_level.pk if datastream.processing_level else None,

        "unitName": datastream.unit.name if datastream.unit else None,
        "unitSymbol": datastream.unit.symbol if datastream.unit else None,
        "observedPropertyName": datastream.observed_property.name if datastream.observed_property else None,
        "sensorName": datastream.sensor.name if datastream.sensor else None,
        "processingLevelName": datastream.processing_level.code if datastream.processing_level else None,
        "isVisible": datastream.is_visible,
        "isPrimaryOwner": association.is_primary_owner if association else False,
        "isStale": is_stale,

        "phenomenonBeginTime": datastream.phenomenon_begin_time,
        "phenomenonEndTime": datastream.phenomenon_end_time,

        "intendedTimeSpacing": datastream.intended_time_spacing if datastream.intended_time_spacing else None,
        "intendedTimeSpacingUnitsId": datastream.intended_time_spacing_units.pk if datastream.intended_time_spacing_units else None,
        "timeAggregationInterval": datastream.time_aggregation_interval,
        "timeAggregationIntervalUnitsId": datastream.time_aggregation_interval_units.pk,

        "dataSourceId": datastream.data_source_id,
        "column": datastream.data_source_column
    }



def get_public_datastreams(thing_id: str):
    try:
        thing = Thing.objects.get(pk=thing_id)
    except Thing.DoesNotExist:
        return JsonResponse({'detail': 'Site not found.'}, status=404)
    return JsonResponse([
        datastream_to_dict(datastream) 
        for datastream in thing.datastreams.all() if datastream.is_visible], safe=False)
