from typing import Optional, List
from datetime import datetime
from sqlalchemy import String, ForeignKey, Column, Table
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


thing_location_association = Table(
    'thing_location',
    Base.metadata,
    Column('thing_id', ForeignKey('thing.id'), primary_key=True),
    Column('location_id', ForeignKey('location.id'), primary_key=True)
)

location_historical_location_association = Table(
    'location_historical_location',
    Base.metadata,
    Column('location_id', ForeignKey('location.id'), primary_key=True),
    Column('historical_location_id', ForeignKey('historical_location.id'), primary_key=True)
)


class Thing(Base):
    __tablename__ = 'thing'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]]
    properties: Mapped[Optional[str]]
    locations: Mapped[List['Location']] = relationship(
        secondary=thing_location_association,
        back_populates='things'
    )
    historical_locations: Mapped[List['HistoricalLocation']] = relationship()


class Location(Base):
    __tablename__ = 'location'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str]
    encoding_type: Mapped[str] = mapped_column(String(255))
    location: Mapped[str]
    properties: Mapped[Optional[str]]
    things: Mapped[List[Thing]] = relationship(
        secondary=thing_location_association,
        back_populates='locations'
    )
    historical_locations: Mapped[List['HistoricalLocation']] = relationship(
        secondary=location_historical_location_association,
        back_populates='locations'
    )


class HistoricalLocation(Base):
    __tablename__ = 'historical_location'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    time: Mapped[datetime]
    thing_id: Mapped[int] = mapped_column(ForeignKey('thing.id'))
    locations: Mapped[List[Location]] = relationship(
        secondary=thing_location_association,
        back_populates='historical_locations'
    )


class Sensor(Base):
    __tablename__ = 'sensor'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str]
    encoding_type: Mapped[str] = mapped_column(String(255))
    sensor_metadata: Mapped[Optional[str]]
    properties: Mapped[Optional[str]]
    datastreams: Mapped[List['Datastream']] = relationship()


class ObservedProperty(Base):
    __tablename__ = 'observed_property'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str]
    definition: Mapped[str]
    properties: Mapped[Optional[str]]
    datastreams: Mapped[List['Datastream']] = relationship()


class FeatureOfInterest(Base):
    __tablename__ = 'feature_of_interest'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str]
    encoding_type: Mapped[str] = mapped_column(String(255))
    feature: Mapped[str]
    properties: Mapped[Optional[str]]


class Datastream(Base):
    __tablename__ = 'datastream'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str]
    unit_of_measurement: Mapped[str]
    observation_type: Mapped[str] = mapped_column(String(255))
    properties: Mapped[Optional[str]]
    observed_area: Mapped[Optional[str]]
    phenomenon_time: Mapped[Optional[datetime]]
    result_time: Mapped[Optional[datetime]]
    thing_id: Mapped[int] = mapped_column(ForeignKey('thing.id'))
    sensor_id: Mapped[int] = mapped_column(ForeignKey('sensor.id'))
    observed_property_id: Mapped[int] = mapped_column(ForeignKey('observed_property.id'))
    observations: Mapped[List['Observation']] = relationship()


class Observation(Base):
    __tablename__ = 'observation'

    datastream_id: Mapped[int] = mapped_column(ForeignKey('datastream.id'), primary_key=True)
    phenomenon_time: Mapped[datetime] = mapped_column(primary_key=True)
    result: Mapped[str] = mapped_column(String(255))
    result_time: Mapped[datetime]
    result_quality: Mapped[Optional[str]] = mapped_column(String(255))
    valid_time: Mapped[Optional[datetime]]
    parameters: Mapped[Optional[str]]
    feature_of_interest_id: Mapped[int] = mapped_column(ForeignKey('feature_of_interest.id'))
