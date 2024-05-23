import pandas as pd
import math
from ninja import Path, File
from ninja.files import UploadedFile
from uuid import UUID
from datetime import datetime
from typing import Optional
from django.db import transaction, IntegrityError
from django.http import StreamingHttpResponse
from django.db.models import Q
from hydroserver.auth import JWTAuth, BasicAuth, anonymous_auth
from core.router import DataManagementRouter
from core.models import Datastream, Observation, Thing, Sensor, ObservedProperty, Unit, ProcessingLevel
from sensorthings.types import ISOTimeString
from core.schemas.datastream import DatastreamFields, DatastreamGetResponse, DatastreamPostBody, DatastreamPatchBody, \
     DatastreamMetadataGetResponse
from core.schemas.unit import UnitGetResponse
from core.schemas.processing_level import ProcessingLevelGetResponse
from core.schemas.observed_property import ObservedPropertyGetResponse
from core.schemas.sensor import SensorGetResponse
from core.utils import generate_csv


router = DataManagementRouter(tags=['Datastreams'])


@router.dm_list('', response=DatastreamGetResponse)
def get_datastreams(
        request,
        modified_since: datetime = None,
        owned_only: Optional[bool] = False,
        primary_owned_only: Optional[bool] = False
):
    """
    Get a list of Datastreams

    This endpoint returns a list of public datastreams and datastreams owned by the authenticated user if there is one.
    """

    datastream_query = Datastream.objects.select_related('processing_level', 'unit', 'time_aggregation_interval_units')
    datastream_query = datastream_query.modified_since(modified_since)
    datastream_query = datastream_query.owner_is_active()

    if primary_owned_only is True:
        datastream_query = datastream_query.primary_owner(user=request.authenticated_user)
    elif owned_only is True:
        datastream_query = datastream_query.owner(user=request.authenticated_user)
    else:
        datastream_query = datastream_query.owner(user=request.authenticated_user, include_public=True)

    if request.authenticated_user and request.authenticated_user.permissions.enabled():
        datastream_query = datastream_query.apply_permissions(user=request.authenticated_user, method='GET')

    datastream_query = datastream_query.distinct()

    response = [
        DatastreamGetResponse.serialize(datastream) for datastream in datastream_query.all()
    ]

    return 200, response


@router.dm_get('{datastream_id}', response=DatastreamGetResponse)
def get_datastream(request, datastream_id: UUID = Path(...)):
    """
    Get details for a Datastream

    This endpoint returns details for a datastream given a datastream ID.
    """

    datastream = Datastream.objects.get_by_id(
        datastream_id=datastream_id,
        user=request.authenticated_user,
        method='GET',
        raise_404=True
    )

    return 200, DatastreamGetResponse.serialize(datastream)


@router.dm_post('', response=DatastreamGetResponse)
@transaction.atomic
def create_datastream(request, data: DatastreamPostBody):
    """
    Create a Datastream

    This endpoint will create a new datastream.
    """

    datastream_data = data.dict(include=set(DatastreamFields.model_fields.keys()))

    thing = Thing.objects.get_by_id(
        thing_id=datastream_data['thing_id'],
        user=request.authenticated_user,
        method='POST',
        model='Datastream',
        raise_404=True
    )

    if not Sensor.objects.get_by_id(
        sensor_id=datastream_data['sensor_id'], user=thing.primary_owner, method='POST', model='Datastream',
        fetch=False
    ):
        return 403, 'You do not have permission to link a datastream to the given sensor.'

    if not ObservedProperty.objects.get_by_id(
        observed_property_id=datastream_data['observed_property_id'], user=thing.primary_owner, method='POST',
        model='Datastream', fetch=False
    ):
        return 403, 'You do not have permission to link a datastream to the given observed property.'

    if not ProcessingLevel.objects.get_by_id(
        processing_level_id=datastream_data['processing_level_id'], user=thing.primary_owner, method='POST',
        model='Datastream', fetch=False
    ):
        return 403, 'You do not have permission to link a datastream to the given processing level.'

    if not Unit.objects.get_by_id(
        unit_id=datastream_data['unit_id'], user=thing.primary_owner, method='POST', model='Datastream',
        fetch=False
    ):
        return 403, 'You do not have permission to link a datastream to the given unit.'

    if not Unit.objects.get_by_id(
        unit_id=datastream_data['time_aggregation_interval_units_id'], user=thing.primary_owner, method='POST',
        model='Datastream', fetch=False
    ):
        return 403, 'You do not have permission to link a datastream to the given time aggregation interval unit.'

    if datastream_data.get('intended_time_spacing_units_id') and not Unit.objects.get_by_id(
        unit_id=datastream_data['intended_time_spacing_units_id'], user=thing.primary_owner, method='POST',
        model='Datastream', fetch=False
    ):
        return 403, 'You do not have permission to link a datastream to the given intended time spacing unit.'

    datastream = Datastream.objects.create(
        **data.dict(include=set(DatastreamFields.model_fields.keys()))
    )

    return 201, DatastreamGetResponse.serialize(datastream)


@router.dm_patch('{datastream_id}', response=DatastreamGetResponse)
@transaction.atomic
def update_datastream(request, data: DatastreamPatchBody, datastream_id: UUID = Path(...)):
    """
    Update a Datastream

    This endpoint will update an existing datastream owned by the authenticated user and return the updated datastream.
    """

    datastream = Datastream.objects.get_by_id(
        datastream_id=datastream_id,
        user=request.authenticated_user,
        method='PATCH',
        raise_404=True
    )

    datastream_data = data.dict(include=set(DatastreamFields.model_fields.keys()), exclude_unset=True)

    if not datastream.primary_owner or (datastream_data.get('thing_id') and not Thing.objects.get_by_id(
        thing_id=datastream_data['thing_id'], user=datastream.primary_owner, method='PATCH', model='Datastream',
        fetch=False
    )):
        return 403, 'You do not have permission to link a datastream to the given thing.'

    if datastream_data.get('sensor_id') and not Sensor.objects.get_by_id(
        sensor_id=datastream_data['sensor_id'], user=datastream.primary_owner, method='PATCH', model='Datastream',
        fetch=False
    ):
        return 403, 'You do not have permission to link a datastream to the given sensor.'

    if datastream_data.get('observed_property_id') and not ObservedProperty.objects.get_by_id(
        observed_property_id=datastream_data['observed_property_id'], user=datastream.primary_owner, method='PATCH',
        model='Datastream', fetch=False
    ):
        return 403, 'You do not have permission to link a datastream to the given observed property.'

    if datastream_data.get('processing_level_id') and not ProcessingLevel.objects.get_by_id(
        processing_level_id=datastream_data['processing_level_id'], user=datastream.primary_owner, method='PATCH',
        model='Datastream', fetch=False
    ):
        return 403, 'You do not have permission to link a datastream to the given processing level.'

    if datastream_data.get('unit_id') and not Unit.objects.get_by_id(
        unit_id=datastream_data['unit_id'], user=datastream.primary_owner, method='PATCH', model='Datastream',
        fetch=False
    ):
        return 403, 'You do not have permission to link a datastream to the given unit.'

    if datastream_data.get('time_aggregation_interval_units_id') and not Unit.objects.get_by_id(
        unit_id=datastream_data['time_aggregation_interval_units_id'], user=datastream.primary_owner, method='PATCH',
        model='Datastream', fetch=False
    ) and not Unit.objects.get_by_id(
        unit_id=datastream_data['time_aggregation_interval_units_id'], user=None, method='PATCH',
        model='Datastream', fetch=False
    ):
        return 403, 'You do not have permission to link a datastream to the given time aggregation interval unit.'

    for field, value in datastream_data.items():
        setattr(datastream, field, value)

    datastream.save()

    return 203, DatastreamGetResponse.serialize(datastream)


@router.dm_delete('{datastream_id}')
def delete_datastream(request, datastream_id: UUID = Path(...)):
    """
    Delete a Datastream

    This endpoint will delete an existing datastream if the authenticated user is the primary owner of the datastream.
    """

    datastream = Datastream.objects.get_by_id(
        datastream_id=datastream_id,
        user=request.authenticated_user,
        method='DELETE',
        raise_404=True
    )

    try:
        datastream.delete()
    except IntegrityError as e:
        return 409, str(e)

    return 204, None


@router.post(
    '{datastream_id}/csv',
    auth=[JWTAuth(), BasicAuth()],
    response={
        201: None,
        400: str,
        401: str,
        403: str,
        404: str,
        409: str
    }
)
@transaction.atomic
def upload_observations(request, datastream_id: UUID = Path(...), file: UploadedFile = File(...)):

    datastream = Datastream.objects.get_by_id(
        datastream_id=datastream_id,
        user=request.authenticated_user,
        method='POST',
        raise_404=True
    )

    dataframe = pd.read_csv(file, dtype={'ResultTime': str, 'Result': float, 'ResultQualifiers': str})

    try:
        dataframe['ISOResultTime'] = dataframe['ResultTime'].apply(
            lambda x: ISOTimeString(x)
        )
    except ValueError:
        return 400, 'Failed to parse uploaded CSV file.'

    dataframe = dataframe[['ISOResultTime', 'Result', 'ResultQualifiers']]

    try:
        Observation.objects.bulk_create([
            Observation(
                datastream_id=datastream.id,
                phenomenon_time=observation['ISOResultTime'],
                result=observation['Result'] if not math.isnan(observation['Result']) else datastream.no_data_value,
                result_qualifiers=observation['ResultQualifiers'].split(',') if observation['ResultQualifiers'] else None
            )
            for observation in dataframe.to_dict(orient='records')
        ])
    except IntegrityError:
        return 409, 'Duplicate phenomenonTime found on this datastream.'

    return 201, None


@router.get(
    '{datastream_id}/csv',
    auth=[JWTAuth(), BasicAuth(), anonymous_auth],
    response={
        200: None,
        403: str,
        404: str
    }
)
def get_datastream_csv(request, datastream_id: UUID = Path(...)):

    datastream = Datastream.objects.get_by_id(
        datastream_id=datastream_id,
        user=request.authenticated_user,
        method='GET',
        raise_404=True
    )

    response = StreamingHttpResponse(generate_csv(datastream), content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="hello_world.csv"'

    return response


@router.get(
    '{datastream_id}/metadata',
    auth=[JWTAuth(), BasicAuth(), anonymous_auth],
    response={
        200: DatastreamMetadataGetResponse,
        403: str,
        404: str
    },
    by_alias=True
)
def get_datastream_metadata(request, datastream_id: UUID = Path(...), include_assignable_metadata: bool = False):

    datastream = Datastream.objects.get_by_id(
        datastream_id=datastream_id,
        user=request.authenticated_user,
        method='GET',
        raise_404=True
    )

    if include_assignable_metadata is True:
        units = Unit.objects.filter(person=datastream.primary_owner).distinct()
        sensors = Sensor.objects.filter(person=datastream.primary_owner).distinct()
        processing_levels = ProcessingLevel.objects.filter(person=datastream.primary_owner).distinct()
        observed_properties = ObservedProperty.objects.filter(person=datastream.primary_owner).distinct()
    else:
        units = Unit.objects.filter(
            Q(datastreams__id=datastream_id) |
            Q(time_aggregation_interval_units__id=datastream_id)
        ).distinct()

        sensors = Sensor.objects.filter(
            Q(datastreams__id=datastream_id)
        ).distinct()

        processing_levels = ProcessingLevel.objects.filter(
            Q(datastreams__id=datastream_id)
        ).distinct()

        observed_properties = ObservedProperty.objects.filter(
            Q(datastreams__id=datastream_id)
        ).distinct()

    return 200, {
        'units': [UnitGetResponse.serialize(unit) for unit in units.all()],
        'sensors': [SensorGetResponse.serialize(sensor) for sensor in sensors.all()],
        'processing_levels': [ProcessingLevelGetResponse.serialize(plv) for plv in processing_levels.all()],
        'observed_properties': [ObservedPropertyGetResponse.serialize(op) for op in observed_properties.all()]
    }
