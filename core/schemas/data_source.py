from ninja import Schema
from typing import Optional, Literal, Union
from pydantic import conint
from datetime import datetime
from uuid import UUID
from hydroserver.schemas import BaseGetResponse, BasePostBody, BasePatchBody


class DataSourceID(Schema):
    id: UUID


class DataSourceFields(Schema):
    name: str
    path: Optional[str] = None
    link: Optional[str] = None
    header_row: Optional[conint(gt=0)] = None
    data_start_row: Optional[conint(gt=0)] = 1
    delimiter: Optional[str] = ','
    quote_char: Optional[str] = '"'
    interval: Optional[conint(gt=0)] = None
    interval_units: Optional[Literal['minutes', 'hours', 'days', 'weeks', 'months']] = None
    crontab: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    paused: Optional[bool]
    timestamp_column: Union[conint(gt=0), str]
    timestamp_format: Optional[str] = '%Y-%m-%dT%H:%M:%S%Z'
    timestamp_offset: Optional[str] = '+0000'
    data_loader_id: UUID
    data_source_thru: Optional[datetime] = None
    last_sync_successful: Optional[bool] = None
    last_sync_message: Optional[str] = None
    last_synced: Optional[datetime] = None
    next_sync: Optional[datetime] = None


class DataSourceGetResponse(BaseGetResponse, DataSourceFields, DataSourceID):

    class Config:
        allow_population_by_field_name = True


class DataSourcePostBody(BasePostBody, DataSourceFields):
    pass


class DataSourcePatchBody(BasePatchBody, DataSourceFields):
    pass
