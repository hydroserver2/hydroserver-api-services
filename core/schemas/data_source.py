from ninja import Schema, Field
from typing import Optional, Literal, Annotated
from pydantic import StringConstraints as StrCon
from datetime import datetime
from uuid import UUID
from hydroserver.schemas import BaseGetResponse, BasePostBody, BasePatchBody


class DataSourceID(Schema):
    id: UUID


class DataSourceFields(Schema):
    name: Annotated[str, StrCon(strip_whitespace=True, max_length=255)]
    path: Optional[Annotated[str, StrCon(strip_whitespace=True, max_length=255)]] = None
    link: Optional[Annotated[str, StrCon(strip_whitespace=True, max_length=255)]] = None
    header_row: Optional[Annotated[int, Field(gt=0, lt=9999)]] = None
    data_start_row: Optional[Annotated[int, Field(gt=0, lt=9999)]] = 1
    delimiter: Optional[Annotated[str, StrCon(strip_whitespace=True, max_length=1)]] = ','
    quote_char: Optional[Annotated[str, StrCon(strip_whitespace=True, max_length=1)]] = '"'
    interval: Optional[Annotated[int, Field(gt=0, lt=9999)]] = None
    interval_units: Optional[Literal['minutes', 'hours', 'days', 'weeks', 'months']] = None
    crontab: Optional[Annotated[str, StrCon(strip_whitespace=True, max_length=255)]] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    paused: Optional[bool]
    timestamp_column: (Annotated[int, Field(gt=0, lt=9999)] |
                       Annotated[str, StrCon(strip_whitespace=True, max_length=255)])
    timestamp_format: Optional[Annotated[str, StrCon(strip_whitespace=True, max_length=255)]] = '%Y-%m-%dT%H:%M:%S%Z'
    timestamp_offset: Optional[Annotated[str, StrCon(strip_whitespace=True, max_length=255)]] = '+0000'
    data_loader_id: UUID
    data_source_thru: Optional[datetime] = None
    last_sync_successful: Optional[bool] = None
    last_sync_message: Optional[Annotated[str, StrCon(strip_whitespace=True)]] = None
    last_synced: Optional[datetime] = None
    next_sync: Optional[datetime] = None


class DataSourceGetResponse(BaseGetResponse, DataSourceFields, DataSourceID):

    class Config:
        allow_population_by_field_name = True


class DataSourcePostBody(BasePostBody, DataSourceFields):
    pass


class DataSourcePatchBody(BasePatchBody, DataSourceFields):
    pass
