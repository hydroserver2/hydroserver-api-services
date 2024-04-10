# from ninja import Schema
# from pydantic import Field
# from typing import Optional, Literal, Union, List
# from uuid import UUID
# from datetime import datetime
# from sensorthings.validators import allow_partial
# from core.endpoints_old.observedproperty.schemas import ObservedPropertyGetResponse
# from core.endpoints_old.processinglevel.schemas import ProcessingLevelGetResponse
# from core.endpoints_old.unit.schemas import UnitGetResponse
# from core.endpoints_old.sensor.schemas import SensorGetResponse
# from core.schemas_old import BasePostBody, BasePatchBody
#
#
# class DatastreamID(Schema):
#     id: UUID
#
#
# class DatastreamFields(Schema):
#     name: Union[UUID, str]
#     description: str
#     observation_type: str = Field(..., alias='observationType')
#     sampled_medium: str = Field(..., alias='sampledMedium')
#     no_data_value: float = Field(..., alias='noDataValue')
#     aggregation_statistic: str = Field(..., alias='aggregationStatistic')
#     time_aggregation_interval: float = Field(..., alias='timeAggregationInterval')
#     status: str = None
#     result_type: str = Field(..., alias='resultType')
#     value_count: int = Field(None, alias='valueCount')
#     phenomenon_begin_time: datetime = Field(None, alias='phenomenonBeginTime')
#     phenomenon_end_time: datetime = Field(None, alias='phenomenonEndTime')
#     result_begin_time: datetime = Field(None, alias='resultBeginTime')
#     result_end_time: datetime = Field(None, alias='resultEndTime')
#     data_source_id: UUID = Field(None, alias='dataSourceId')
#     data_source_column: str = Field(None, alias='dataSourceColumn')
#     is_visible: bool = Field(True, alias='isVisible')
#     is_data_visible: bool = Field(True, alias='isDataVisible')
#     thing_id: UUID = Field(..., alias='thingId')
#     sensor_id: UUID = Field(..., alias='sensorId')
#     observed_property_id: UUID = Field(..., alias='observedPropertyId')
#     processing_level_id: UUID = Field(..., alias='processingLevelId')
#     unit_id: UUID = Field(..., alias='unitId')
#     time_aggregation_interval_units_id: UUID = Field(..., alias='timeAggregationIntervalUnitsId')
#     intended_time_spacing: float = Field(None, alias='intendedTimeSpacing')
#     intended_time_spacing_units: Optional[Literal['seconds', 'minutes', 'hours', 'days']] = \
#         Field(None, alias='intendedTimeSpacingUnits')
#
#
# class DatastreamGetResponse(DatastreamFields, DatastreamID):
#
#     class Config:
#         allow_population_by_field_name = True
#
#
# class DatastreamPostBody(BasePostBody, DatastreamFields):
#     pass
#
#
# @allow_partial
# class DatastreamPatchBody(BasePatchBody, DatastreamFields):
#     thing_id: UUID = Field(..., alias='thingId')
#
#
# class DatastreamMetadataGetResponse(Schema):
#     units: List[UnitGetResponse]
#     sensors: List[SensorGetResponse]
#     processing_levels: List[ProcessingLevelGetResponse] = Field(..., alias='processingLevels')
#     observed_properties: List[ObservedPropertyGetResponse] = Field(..., alias='observedProperties')
#
#     class Config:
#         allow_population_by_field_name = True
