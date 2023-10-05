from ninja import Schema
from pydantic import Field
from typing import Union
from uuid import UUID
from datetime import datetime
from sensorthings.validators import allow_partial


class DatastreamID(Schema):
    id: UUID


class DatastreamFields(Schema):
    name: Union[UUID, str]
    description: str
    observation_type: str = Field(..., alias='observationType')
    sampled_medium: str = Field(..., alias='sampledMedium')
    no_data_value: str = Field(..., alias='noDataValue')
    aggregation_statistic: str = Field(..., alias='aggregationStatistic')
    time_aggregation_interval: str = Field(..., alias='timeAggregationInterval')
    status: str = None
    result_type: str = Field(None, alias='resultType')
    value_count: str = Field(None, alias='valueCount')
    intended_time_spacing: str = Field(None, alias='intendedTimeSpacing')
    phenomenon_begin_time: datetime = Field(None, alias='phenomenonBeginTime')
    phenomenon_end_time: datetime = Field(None, alias='phenomenonEndTime')
    result_begin_time: datetime = Field(None, alias='resultBeginTime')
    result_end_time: datetime = Field(None, alias='resultEndTime')
    data_source_id: UUID = Field(None, alias='dataSourceId')
    data_source_column: str = Field(None, alias='dataSourceColumn')
    is_visible: bool = Field(True, alias='isVisible')
    thing_id: UUID = Field(..., alias='thingId')
    sensor_id: UUID = Field(..., alias='sensorId')
    observed_property_id: UUID = Field(..., alias='observedPropertyId')
    processing_level_id: UUID = Field(..., alias='processingLevelId')
    unit_id: UUID = Field(..., alias='unitId')
    time_aggregation_interval_units_id: UUID = Field(..., alias='timeAggregationIntervalUnitsId')
    intended_time_spacing_units_id: UUID = Field(None, alias='intendedTimeSpacingUnitsId')


class DatastreamGetResponse(DatastreamFields, DatastreamID):

    class Config:
        allow_population_by_field_name = True


class DatastreamPostBody(DatastreamFields):
    pass


@allow_partial
class DatastreamPatchBody(DatastreamFields):
    thing_id: UUID = Field(..., alias='thingId')