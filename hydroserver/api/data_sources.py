from hydroserver.api.api import api
from django.db import transaction
from django.http import HttpRequest
from typing import List
from hydroserver.api.authentication import BasicAuth
from hydroserver.api.util import jwt_auth, transform_data_source
from hydroserver.schemas import *
from sites.models import Datastream, DataSource, DataSourceOwner


@api.get(
    '/data-sources',
    url_name='get_data_sources',
    response={
        200: List[DataSourceGetResponse]
    },
    auth=[BasicAuth(), jwt_auth]
)
def get_data_sources(request: HttpRequest):

    data_sources = DataSource.objects.filter(datasourceowner__person=request.authenticated_user)

    return [
        transform_data_source(data_source) for data_source in data_sources
    ]


@api.get(
    '/data-sources/{data_source_id}',
    url_name='get_data_source',
    response={
        200: DataSourceGetResponse,
        404: None
    },
    auth=[BasicAuth(), jwt_auth]
)
def get_data_source(request: HttpRequest, data_source_id: str):

    data_source = DataSource.objects.get(datasourceowner__person=request.authenticated_user, pk=data_source_id)

    return transform_data_source(data_source)


@api.post(
    '/data-sources',
    url_name='create_data_source',
    response={
        201: None
    },
    auth=[BasicAuth(), jwt_auth]
)
@transaction.atomic
def post_data_source(request: HttpRequest, data_source: DataSourcePostBody):
    """"""

    new_data_source = DataSource.objects.create(
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

    DataSourceOwner.objects.create(
        data_source=new_data_source,
        person=request.authenticated_user
    )

    for datastream in data_source.datastreams:

        datastream_db = Datastream.objects.get(pk=datastream.datastream_id)
        request.authenticated_user.thing_associations.get(
            thing=datastream_db.thing,
            owns_thing=True
        )
        datastream_db.data_source = new_data_source
        datastream_db.data_source_column = datastream.column
        datastream_db.save()

    return None


@api.patch(
    '/data-sources/{data_source_id}',
    url_name='update_data_source',
    response={
        204: None
    },
    auth=[BasicAuth(), jwt_auth],
)
@transaction.atomic
def patch_data_source(request: HttpRequest, data_source_id: str, data_source: DataSourcePatchBody):
    """"""

    data_source = data_source.dict(exclude_unset=True)
    data_source_db = DataSource.objects.filter(
        pk=data_source_id,
        datasourceowner__person=request.authenticated_user,
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
        datastream_db = Datastream.objects.get(pk=datastream['datastream_id'])
        request.authenticated_user.thing_associations.get(
            thing=datastream_db.thing,
            owns_thing=True
        )
        datastream_db.data_source = data_source_db
        datastream_db.data_source_column = datastream['column']
        datastream_db.save()


@api.delete(
    '/data-sources/{data_source_id}',
    auth=[BasicAuth(), jwt_auth],
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

    if request.authenticated_user not in [
        data_source_owner.person for data_source_owner
        in data_source.datasourceowner_set.filter(is_primary_owner=True)
    ]:
        return 403, 'You do not have permission to delete this data source.'

    data_source.delete()

    return 200
