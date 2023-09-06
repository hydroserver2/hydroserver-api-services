from django.http import HttpRequest
from django.db import transaction

from ninja import Schema, Router
from pydantic import conint

from typing import Optional, List, Union
from uuid import UUID
from datetime import datetime

from .data_loader import DataLoaderGetResponse
from hydroloader import HydroLoaderConf, HydroLoaderConfFileTimestamp, HydroLoaderConfSchedule, \
     HydroLoaderConfFileAccess
from sensorthings.validators import allow_partial
from core.models import Datastream, DataSource
from accounts.auth import BasicAuth, JWTAuth

router = Router(tags=['Data Sources'])


class DataSourceDatastream(Schema):
    id: UUID
    name: str
    description: str
    phenomenon_start_time: Optional[datetime]
    phenomenon_end_time: Optional[datetime]
    column: Optional[Union[int, str]]


class DataSourceGetResponse(HydroLoaderConf):
    id: UUID
    name: str
    datastreams: List[DataSourceDatastream]
    data_loader: Optional[DataLoaderGetResponse]
    data_source_thru: Optional[datetime]
    last_sync_successful: Optional[bool]
    last_sync_message: Optional[str]
    last_synced: Optional[datetime]
    next_sync: Optional[datetime]
    database_thru_upper: Optional[datetime]
    database_thru_lower: Optional[datetime]


class DataSourcePostBody(HydroLoaderConf):
    name: str
    data_loader: Optional[UUID]
    data_source_thru: Optional[datetime]
    last_sync_successful: Optional[bool]
    last_sync_message: Optional[str]
    last_synced: Optional[datetime]
    next_sync: Optional[datetime]


class HydroLoaderConfFileDatastreamPatch(Schema):
    id: UUID
    column: Optional[Union[conint(gt=0), str]]


@allow_partial
class DataSourcePatchBody(HydroLoaderConf):
    name: str
    data_loader: Optional[UUID]
    data_source_thru: Optional[datetime]
    last_sync_successful: Optional[bool]
    last_sync_message: Optional[str]
    last_synced: Optional[datetime]
    next_sync: Optional[datetime]
    datastreams: List[HydroLoaderConfFileDatastreamPatch]


@router.get(
    '',
    url_name='get_data_sources',
    response={
        200: List[DataSourceGetResponse]
    },
    auth=[BasicAuth(), JWTAuth()]
)
def get_data_sources(request: HttpRequest):

    data_sources = DataSource.objects.filter(person=getattr(request, 'authenticated_user'))

    return [
        transform_data_source(data_source) for data_source in data_sources
    ]


@router.get(
    '/{data_source_id}',
    url_name='get_data_source',
    response={
        200: DataSourceGetResponse,
        404: None
    },
    auth=[BasicAuth(), JWTAuth()]
)
def get_data_source(request: HttpRequest, data_source_id: str):

    data_source = DataSource.objects.get(
        person=getattr(request, 'authenticated_user'),
        pk=data_source_id
    )

    return transform_data_source(data_source)


@router.post(
    '',
    url_name='create_data_source',
    response={
        201: None
    },
    auth=[BasicAuth(), JWTAuth()]
)
@transaction.atomic
def post_data_source(request: HttpRequest, data_source: DataSourcePostBody):
    """"""

    new_data_source = DataSource.objects.create(
        person=getattr(request, 'authenticated_user'),
        name=data_source.name,
        data_loader_id=data_source.data_loader,
        path=data_source.file_access.path,
        url=data_source.file_access.url,
        header_row=data_source.file_access.header_row,
        data_start_row=data_source.file_access.data_start_row,
        delimiter=data_source.file_access.delimiter,
        quote_char=data_source.file_access.quote_char,
        interval=data_source.schedule.interval,
        interval_units=data_source.schedule.interval_units,
        crontab=data_source.schedule.crontab,
        start_time=data_source.schedule.start_time,
        end_time=data_source.schedule.end_time,
        paused=data_source.schedule.paused if data_source.schedule.paused is not None else False,
        timestamp_column=data_source.file_timestamp.column,
        timestamp_format=data_source.file_timestamp.format,
        timestamp_offset=data_source.file_timestamp.offset,
        data_source_thru=data_source.data_source_thru,
        last_sync_successful=data_source.last_sync_successful,
        last_sync_message=data_source.last_sync_message,
        last_synced=data_source.last_synced,
        next_sync=data_source.next_sync
    )

    for datastream in data_source.datastreams:
        authenticated_user = getattr(request, 'authenticated_user')
        datastream_db = Datastream.objects.get(pk=getattr(datastream, 'datastream_id'))
        authenticated_user.thing_associations.get(
            thing=datastream_db.thing,
            owns_thing=True
        )
        datastream_db.data_source = new_data_source
        datastream_db.data_source_column = datastream.column
        datastream_db.save()

    return None


@router.patch(
    '/{data_source_id}',
    url_name='update_data_source',
    response={
        204: None
    },
    auth=[BasicAuth(), JWTAuth()],
)
@transaction.atomic
def patch_data_source(request: HttpRequest, data_source_id: str, data_source: DataSourcePatchBody):
    """"""

    data_source = data_source.dict(exclude_unset=True)
    data_source_db = DataSource.objects.filter(
        pk=data_source_id,
        person=getattr(request, 'authenticated_user'),
    )[0]

    if 'name' in data_source:
        data_source_db.name = data_source['name']
    if 'data_loader' in data_source:
        data_source_db.data_loader_id = data_source['data_loader']
    if 'data_source_thru' in data_source:
        data_source_db.data_source_thru = data_source['data_source_thru']
    if 'last_sync_successful' in data_source:
        data_source_db.last_sync_successful = data_source['last_sync_successful']
    if 'last_sync_message' in data_source:
        data_source_db.last_sync_message = data_source['last_sync_message']
    if 'last_synced' in data_source:
        data_source_db.last_synced = data_source['last_synced']
    if 'next_sync' in data_source:
        data_source_db.next_sync = data_source['next_sync']

    if 'path' in data_source.get('file_access', {}):
        data_source_db.path = data_source['file_access']['path']
    if 'url' in data_source.get('file_access', {}):
        data_source_db.url = data_source['file_access']['url']
    if 'header_row' in data_source.get('file_access', {}):
        data_source_db.header_row = data_source['file_access']['header_row']
    if 'data_start_row' in data_source.get('file_access', {}):
        data_source_db.data_start_row = data_source['file_access']['data_start_row']
    if 'delimiter' in data_source.get('file_access', {}):
        data_source_db.delimiter = data_source['file_access']['delimiter']
    if 'quote_char' in data_source.get('file_access', {}):
        data_source_db.quote_char = data_source['file_access']['quote_char']

    if 'interval' in data_source.get('schedule', {}):
        data_source_db.interval = data_source['schedule']['interval']
    if 'interval_units' in data_source.get('schedule', {}):
        data_source_db.interval_units = data_source['schedule']['interval_units']
    if 'crontab' in data_source.get('schedule', {}):
        data_source_db.crontab = data_source['schedule']['crontab']
    if 'start_time' in data_source.get('schedule', {}):
        data_source_db.start_time = data_source['schedule']['start_time']
    if 'end_time' in data_source.get('schedule', {}):
        data_source_db.end_time = data_source['schedule']['end_time']
    if 'paused' in data_source.get('schedule', {}):
        data_source_db.paused = data_source['schedule']['paused'] if data_source['schedule']['paused'] \
                                                                     is not None else False

    if 'column' in data_source.get('file_timestamp', {}):
        data_source_db.timestamp_column = data_source['file_timestamp']['column']
    if 'format' in data_source.get('file_timestamp', {}):
        data_source_db.timestamp_format = data_source['file_timestamp']['format']
    if 'offset' in data_source.get('file_timestamp', {}):
        data_source_db.timestamp_offset = data_source['file_timestamp']['offset']

    data_source_db.save()

    for datastream in data_source.get('datastreams', []):
        authenticated_user = getattr(request, 'authenticated_user')
        datastream_db = Datastream.objects.get(pk=datastream['id'])
        authenticated_user.thing_associations.get(
            thing=datastream_db.thing,
            owns_thing=True
        )
        datastream_db.data_source = data_source_db
        datastream_db.data_source_column = datastream['column']
        datastream_db.save()


@router.delete(
    '/{data_source_id}',
    auth=[BasicAuth(), JWTAuth()],
    response={
        200: None,
        403: None,
        404: None
    },
)
def delete_data_source(request: HttpRequest, data_source_id: str):
    try:
        data_source = DataSource.objects.get(id=data_source_id)
    except DataSource.DoesNotExist:
        return 404, f'Data Source with ID: {data_source_id} does not exist.'

    if data_source.person != getattr(request, 'authenticated_user'):
        return 403, 'You do not have permission to delete this data source.'

    data_source.delete()

    return 200


def transform_data_source(data_source):
    return DataSourceGetResponse(
        id=data_source.id,
        name=data_source.name,
        data_source_thru=data_source.data_source_thru,
        last_sync_successful=data_source.last_sync_successful,
        last_sync_message=data_source.last_sync_message,
        last_synced=data_source.last_synced,
        next_sync=data_source.next_sync,
        data_loader=DataLoaderGetResponse(
            id=data_source.data_loader.id,
            name=data_source.data_loader.name
        ) if data_source.data_loader else None,
        database_thru_upper=max([
            datastream.phenomenon_end_time for datastream in data_source.datastream_set.all()
            if datastream.phenomenon_end_time is not None
        ], default=None),
        database_thru_lower=min([
            datastream.phenomenon_end_time for datastream in data_source.datastream_set.all()
            if datastream.phenomenon_end_time is not None
        ], default=None),
        file_access=HydroLoaderConfFileAccess(
            path=data_source.path,
            url=data_source.url,
            header_row=data_source.header_row,
            data_start_row=data_source.data_start_row,
            delimiter=data_source.delimiter,
            quote_char=data_source.quote_char
        ),
        schedule=HydroLoaderConfSchedule(
            crontab=data_source.crontab,
            interval=data_source.interval,
            interval_units=data_source.interval_units,
            start_time=data_source.start_time,
            end_time=data_source.end_time,
            paused=data_source.paused
        ),
        file_timestamp=HydroLoaderConfFileTimestamp(
            column=data_source.timestamp_column,
            format=data_source.timestamp_format,
            offset=data_source.timestamp_offset
        ),
        datastreams=[
            DataSourceDatastream(
                id=datastream.id,
                name=str(datastream.name),
                description=datastream.description,
                phenomenon_start_time=datastream.phenomenon_begin_time,
                phenomenon_end_time=datastream.phenomenon_end_time,
                column=datastream.data_source_column
            ) for datastream in data_source.datastream_set.all()
        ]
    )
