from uuid import UUID
from odmst.sa_types import GUID
from typing import Optional
from datetime import datetime
from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    type_annotation_map = {
        UUID: GUID
    }


class CV:
    name: Mapped[str] = mapped_column(String(255), primary_key=True)
    definition: Mapped[str]
    link: Mapped[Optional[str]] = mapped_column(String(255))


class OrganizationTypeCV(Base, CV):
    __tablename__ = 'organization_type_cv'


class MethodTypeCV(Base, CV):
    __tablename__ = 'method_type_cv'


class SamplingFeatureTypeCV(Base, CV):
    __tablename__ = 'sampling_feature_type_cv'


class SiteTypeCV(Base, CV):
    __tablename__ = 'site_type_cv'


class ElevationDatumCV(Base, CV):
    __tablename__ = 'elevation_datum_cv'


class ObservationTypeCV(Base, CV):
    __tablename__ = 'observation_type_cv'


class ResultTypeCV(Base, CV):
    __tablename__ = 'result_type_cv'


class StatusCV(Base, CV):
    __tablename__ = 'status_cv'


class SampledMediumCV(Base, CV):
    __tablename__ = 'sampled_medium_cv'


class AggregationStatisticCV(Base, CV):
    __tablename__ = 'aggregation_statistic_cv'


class UnitTypeCV(Base, CV):
    __tablename__ = 'unit_type_cv'


class VariableTypeCV(Base, CV):
    __tablename__ = 'variable_type_cv'


class ResultQualityCV(Base, CV):
    __tablename__ = 'result_quality_cv'


class Thing(Base):
    __tablename__ = 'thing'

    uuid: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str]
    sampling_feature_code: Mapped[str] = mapped_column(String(255))
    sampling_feature_type: Mapped[str] = mapped_column(ForeignKey('sampling_feature_type_cv.name'))
    site_type: Mapped[str] = mapped_column(ForeignKey('site_type_cv.name'))
    latitude: Mapped[float]
    longitude: Mapped[float]
    elevation_m: Mapped[Optional[float]]
    elevation_datum: Mapped[Optional[str]] = mapped_column(ForeignKey('elevation_datum_cv.name'))
    state: Mapped[Optional[str]] = mapped_column(String(255))
    county: Mapped[Optional[str]] = mapped_column(String(255))


class SensorModel(Base):
    __tablename__ = 'sensor_model'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(255))
    link: Mapped[Optional[str]] = mapped_column(String(255))
    manufacturer_name: Mapped[str] = mapped_column(String(255))


class Sensor(Base):
    __tablename__ = 'sensor'

    uuid: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str]
    method_code: Mapped[Optional[str]] = mapped_column(String(255))
    method_type: Mapped[str] = mapped_column(ForeignKey('method_type_cv.name'))
    method_link: Mapped[Optional[str]] = mapped_column(String(255))
    sensor_model_id: Mapped[Optional[int]] = mapped_column(ForeignKey('sensor_model.id'))


class ProcessingLevel(Base):
    __tablename__ = 'processing_level'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(255))
    definition: Mapped[Optional[str]]
    explanation: Mapped[Optional[str]]


class Unit(Base):
    __tablename__ = 'unit'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    symbol: Mapped[str] = mapped_column(String(255))
    definition: Mapped[str]
    unit_type: Mapped[str] = mapped_column(ForeignKey('unit_type_cv.name'))


class ObservedProperty(Base):
    __tablename__ = 'observed_property'

    uuid: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(ForeignKey('variable_type_cv.name'))
    definition: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(255))
    variable_code: Mapped[str] = mapped_column(String(255))
    variable_type: Mapped[str] = mapped_column(ForeignKey('variable_type_cv.name'))


class Datastream(Base):
    __tablename__ = 'datastream'

    uuid: Mapped[UUID] = mapped_column(primary_key=True)
    sensor_uuid: Mapped[UUID] = mapped_column(ForeignKey('sensor.uuid'))
    thing_uuid: Mapped[UUID] = mapped_column(ForeignKey('thing.uuid'))
    observed_property_uuid: Mapped[UUID] = mapped_column(ForeignKey('observed_property.uuid'))
    unit_id: Mapped[int] = mapped_column(ForeignKey('unit.id'))
    observation_type: Mapped[str] = mapped_column(ForeignKey('observation_type_cv.name'))
    result_type: Mapped[str] = mapped_column(ForeignKey('result_type_cv.name'))
    status: Mapped[Optional[str]] = mapped_column(ForeignKey('status_cv.name'))
    sampled_medium: Mapped[str] = mapped_column(ForeignKey('sampled_medium_cv.name'))
    value_count: Mapped[Optional[int]]
    no_data_value: Mapped[float]
    processing_level_id: Mapped[int] = mapped_column(ForeignKey('processing_level.id'))
    intended_time_spacing: Mapped[Optional[float]]
    intended_time_spacing_unit_id: Mapped[Optional[int]] = mapped_column(ForeignKey('unit.id'))
    aggregation_statistic: Mapped[str] = mapped_column(ForeignKey('aggregation_statistic_cv.name'))
    time_aggregation_interval: Mapped[float]
    time_aggregation_interval_unit_id: Mapped[int] = mapped_column(ForeignKey('unit.id'))
    phenomenon_begin_time: Mapped[Optional[datetime]]
    phenomenon_end_time: Mapped[Optional[datetime]]


class Observation(Base):
    __tablename__ = 'observation'

    uuid: Mapped[UUID] = mapped_column(primary_key=True)
    datastream_uuid: Mapped[UUID] = mapped_column(ForeignKey('datastream.uuid'), primary_key=True)
    phenomenon_time: Mapped[datetime] = mapped_column(primary_key=True)
    result: Mapped[float]
    result_quality: Mapped[Optional[str]] = mapped_column(ForeignKey('result_quality_cv.name'))
    valid_begin_time: Mapped[Optional[datetime]]
    valid_end_time: Mapped[Optional[datetime]]

    __table_args__ = (
        UniqueConstraint('datastream_uuid', 'phenomenon_time', name='_datastream_uuid_phenomenon_time_uc'),
    )
