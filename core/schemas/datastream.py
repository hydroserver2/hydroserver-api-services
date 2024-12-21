from ninja import Schema, Field
from pydantic import ConfigDict, StringConstraints as StrCon
from typing import Optional, Literal, List, Annotated
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
    name: UUID | Annotated[str, StrCon(strip_whitespace=True, max_length=255)]
    description: Annotated[str, StrCon(strip_whitespace=True)]
    observation_type: Annotated[str, StrCon(strip_whitespace=True, max_length=255)]
    sampled_medium: Annotated[str, StrCon(strip_whitespace=True, max_length=255)]
    no_data_value: float
    aggregation_statistic: Annotated[str, StrCon(strip_whitespace=True, max_length=255)]
    time_aggregation_interval: float
    status: Optional[Annotated[str, StrCon(strip_whitespace=True, max_length=255)]] = None
    result_type: Annotated[str, StrCon(strip_whitespace=True, max_length=255)]
    value_count: Optional[Annotated[int, Field(ge=0)]] = None
    phenomenon_begin_time: Optional[datetime] = None
    phenomenon_end_time: Optional[datetime] = None
    result_begin_time: Optional[datetime] = None
    result_end_time: Optional[datetime] = None
    data_source_id: Optional[UUID] = None
    data_source_column: Optional[Annotated[str, StrCon(strip_whitespace=True, max_length=255)]] = None
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
    model_config = ConfigDict(populate_by_name=True)


class DatastreamPostBody(BasePostBody, DatastreamFields):
    pass


class DatastreamPatchBody(BasePatchBody, DatastreamFields):
    pass


class DatastreamMetadataGetResponse(Schema):
    model_config = ConfigDict(populate_by_name=True)

    units: List[UnitGetResponse]
    sensors: List[SensorGetResponse]
    processing_levels: List[ProcessingLevelGetResponse]
    observed_properties: List[ObservedPropertyGetResponse]
