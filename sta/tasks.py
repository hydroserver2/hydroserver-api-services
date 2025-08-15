from typing import Optional
from psycopg.errors import UniqueViolation
from ninja.errors import HttpError
from django_tasks import task
from django.db import transaction
from django.db.utils import IntegrityError
from sta.models import Observation, Datastream
from sta.services.datastream import DatastreamService

datastream_service = DatastreamService()


@task()
@transaction.atomic
def copy_observations(
    source_datastream_id: str,
    destination_datastream_id: str,
    phenomenon_time_start: Optional[str] = None,
    phenomenon_time_end: Optional[str] = None,
):
    try:
        destination_datastream = Datastream.objects.get(id=destination_datastream_id)
    except Datastream.DoesNotExist:
        raise HttpError(404, "Destination datastream does not exist")

    queryset = Observation.objects.filter(datastream_id=source_datastream_id)

    if phenomenon_time_start is not None:
        queryset = queryset.filter(phenomenon_time__gte=phenomenon_time_start)

    if phenomenon_time_end is not None:
        queryset = queryset.filter(phenomenon_time__lte=phenomenon_time_end)

    fields = [f.name for f in Observation._meta.fields if f.name not in ["id", "datastream"]]

    observations = [
        Observation(
            datastream=destination_datastream,
            **observation
        )
        for observation in queryset.values(*fields)
    ]

    try:
        Observation.objects.bulk_copy(observations)
    except (
        IntegrityError,
        UniqueViolation,
    ):
        raise HttpError(409, "Duplicate phenomenonTime found on this datastream.")

    datastream_service.update_observation_statistics(
        datastream=destination_datastream,
        fields=["phenomenon_begin_time", "phenomenon_end_time", "value_count"],
    )
