from ninja import Schema, Field
from typing import Optional, Literal, Union
from pydantic import conint
from datetime import datetime
from uuid import UUID
from sensorthings.validators import disable_required_field_validation
from core.schemas import BasePostBody, BasePatchBody


class DataSourceID(Schema):
    id: UUID


class DataSourceFields(Schema):
    name: str
    path: Optional[str]
    url: Optional[str]
    header_row: Optional[conint(gt=0)] = Field(None, alias='headerRow')
    data_start_row: Optional[conint(gt=0)] = Field(1, alias='dataStartRow')
    delimiter: Optional[str] = ','
    quote_char: Optional[str] = Field('"', alias='quoteChar')
    interval: Optional[conint(gt=0)]
    interval_units: Optional[Literal['minutes', 'hours', 'days', 'weeks', 'months']] = \
        Field(None, alias='intervalUnits')
    crontab: Optional[str]
    start_time: Optional[datetime] = Field(None, alias='startTime')
    end_time: Optional[datetime] = Field(None, alias='endTime')
    paused: Optional[bool]
    timestamp_column: Union[conint(gt=0), str] = Field(..., alias='timestampColumn')
    timestamp_format: Optional[str] = Field('%Y-%m-%dT%H:%M:%S%Z', alias='timestampFormat')
    timestamp_offset: Optional[str] = Field('+0000', alias='timestampOffset')
    data_loader_id: UUID = Field(..., alias='dataLoaderId')
    data_source_thru: Optional[datetime] = Field(None, alias='dataSourceThru')
    last_sync_successful: Optional[bool] = Field(None, alias='lastSyncSuccessful')
    last_sync_message: Optional[str] = Field(None, alias='lastSyncMessage')
    last_synced: Optional[datetime] = Field(None, alias='lastSynced')
    next_sync: Optional[datetime] = Field(None, alias='nextSync')


class DataSourceGetResponse(DataSourceFields, DataSourceID):

    @classmethod
    def serialize(cls, data_source):  # Temporary until after Pydantic v2 update
        return {
            'id': data_source.id,
            **{field: getattr(data_source, field) for field in DataSourceFields.model_fields.keys()},
        }

    class Config:
        allow_population_by_field_name = True


class DataSourcePostBody(BasePostBody, DataSourceFields):
    pass


@disable_required_field_validation
class DataSourcePatchBody(BasePatchBody, DataSourceFields):
    pass
