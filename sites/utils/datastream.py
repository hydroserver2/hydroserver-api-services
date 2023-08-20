from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from sites.models import Observation, Thing
import math

def datastream_to_dict(datastream, association=None, add_recent_observations=True):
    observation_list = []
    most_recent_observation = None
    is_stale = True
    if add_recent_observations:
        if datastream.result_end_time:
            if datastream.result_end_time > timezone.now() - timedelta(hours=72):
                is_stale = False
            since_time = datastream.result_end_time - timedelta(hours=72)
            observations = Observation.objects.filter(datastream=datastream, result_time__gte=since_time).order_by('-result_time')
            for observation in observations:
                observation_list.append({
                    "id": observation.id,
                    "result": observation.result if not math.isnan(observation.result) else None,
                    "result_time": observation.result_time,
                })
            if observation_list:
                most_recent_observation = observation_list[0]

    return {
        "id": datastream.pk,
        "thing_id": datastream.thing.id,
        "observation_type": datastream.observation_type,
        "result_type": datastream.result_type,
        "status": datastream.status,
        "sampled_medium": datastream.sampled_medium,
        "no_data_value": datastream.no_data_value,
        "aggregation_statistic": datastream.aggregation_statistic,
        "observations": observation_list if observation_list else None,
        "most_recent_observation": most_recent_observation,

        "unit_id": datastream.unit.pk if datastream.unit else None,
        "observed_property_id": datastream.observed_property.pk if datastream.observed_property else None,
        "method_id": datastream.sensor.pk if datastream.sensor else None,
        "processing_level_id": datastream.processing_level.pk if datastream.processing_level else None,

        "unit_name": datastream.unit.name if datastream.unit else None,
        "unit_symbol": datastream.unit.symbol if datastream.unit else None,
        "observed_property_name": datastream.observed_property.name if datastream.observed_property else None,
        "method_name": datastream.sensor.name if datastream.sensor else None,
        "processing_level_name": datastream.processing_level.processing_level_code if datastream.processing_level else None,
        "is_visible": datastream.is_visible,
        "is_primary_owner": association.is_primary_owner if association else False,
        "is_stale": is_stale,

        "data_source_id": datastream.data_source_id,
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
