from ninja import Schema
from typing import Optional, Literal, Union, List
from uuid import UUID
from datetime import datetime
from core.schemas.observed_property import ObservedPropertyGetResponse
from core.schemas.processing_level import ProcessingLevelGetResponse
from core.schemas.unit import UnitGetResponse
from core.schemas.sensor import SensorGetResponse
from hydroserver.schemas import BaseGetResponse, BasePostBody, BasePatchBody


class DatastreamID(Schema):
    id: UUID


class DatastreamFields(Schema):
    name: Union[UUID, str]
    description: str
    observation_type: str
    sampled_medium: str
    no_data_value: float
    aggregation_statistic: str
    time_aggregation_interval: float
    status: Optional[str] = None
    result_type: str
    value_count: Optional[int] = None
    phenomenon_begin_time: Optional[datetime] = None
    phenomenon_end_time: Optional[datetime] = None
    result_begin_time: Optional[datetime] = None
    result_end_time: Optional[datetime] = None
    data_source_id: Optional[UUID] = None
    data_source_column: Optional[str] = None
    is_visible: bool = True
    is_data_visible: bool = True
    thing_id: UUID
    sensor_id: UUID
    observed_property_id: UUID
    processing_level_id: UUID
    unit_id: UUID
    time_aggregation_interval_units: Literal['seconds', 'minutes', 'hours', 'days']
    intended_time_spacing: Optional[float] = None
    intended_time_spacing_units: Optional[Literal['seconds', 'minutes', 'hours', 'days']] = None


class DatastreamGetResponse(BaseGetResponse, DatastreamFields, DatastreamID):

    class Config:
        allow_population_by_field_name = True


class DatastreamPostBody(BasePostBody, DatastreamFields):
    pass


class DatastreamPatchBody(BasePatchBody, DatastreamFields):
    pass


class DatastreamMetadataGetResponse(Schema):
    units: List[UnitGetResponse]
    sensors: List[SensorGetResponse]
    processing_levels: List[ProcessingLevelGetResponse]
    observed_properties: List[ObservedPropertyGetResponse]

    class Config:
        allow_population_by_field_name = True
