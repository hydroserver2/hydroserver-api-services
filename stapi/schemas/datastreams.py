from ninja import Schema, Field
from pydantic import ConfigDict
from typing import List, Union, Optional
from datetime import datetime
from sensorthings.components.datastreams.schemas import (DatastreamGetResponse as DefaultDatastreamGetResponse,
                                                         DatastreamListResponse as DefaultDatastreamListResponse)


class DatastreamProperties(Schema):
    model_config = ConfigDict(populate_by_name=True)

    result_type: str = Field(..., alias='resultType')
    status: Union[str, None] = None
    sampled_medium: str = Field(..., alias='sampledMedium')
    value_count: Union[int, None] = Field(None, alias='valueCount')
    no_data_value: float = Field(..., alias='noDataValue')
    processing_level_code: str = Field(..., alias='processingLevelCode')
    intended_time_spacing: Union[float, None] = Field(None, alias='intendedTimeSpacing')
    intended_time_spacing_units: Union[str, None] = Field(None, alias='intendedTimeSpacingUnitOfMeasurement')
    aggregation_statistic: Union[str, None] = Field(None, alias='aggregationStatistic')
    time_aggregation_interval: float = Field(None, alias='timeAggregationInterval')
    time_aggregation_interval_units: str = Field(..., alias='timeAggregationIntervalUnitOfMeasurement')
    last_updated: Optional[datetime] = Field(None, alias='lastUpdated')


class DatastreamGetResponse(DefaultDatastreamGetResponse):
    observation_type: str = Field(..., alias='observationType')
    properties: DatastreamProperties


class DatastreamListResponse(DefaultDatastreamListResponse):
    value: List[DatastreamGetResponse]
