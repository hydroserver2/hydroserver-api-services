from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime, LargeBinary
# from sqlalchemy.dialects.postgresql import JSONB
# from sqlalchemy_json import mutable_json_type
from sqlalchemy.orm import relationship

Base = declarative_base()


ThingLocation = Table(
    'thing_location',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('thing_id', Integer, ForeignKey('thing.id')),
    Column('location_id', Integer, ForeignKey('location.id'))
)


class Thing(Base):
    __tablename__ = 'thing'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    # properties = Column(mutable_json_type(dbtype=JSONB, nested=True), nullable=True)
    locations = relationship('Location', secondary=ThingLocation, backref='things')
    historical_locations = relationship('HistoricalLocation', backref='thing')


class LocationEncodingType(Base):
    __tablename__ = 'location_encoding_type'

    code = Column(String, primary_key=True)
    name = Column(String)


class Location(Base):
    __tablename__ = 'location'

    id = Column(Integer, primary_key=True)
    description = Column(String)
    encoding_type = Column(String, ForeignKey('location_encoding_type.code'))
    # location = Column(mutable_json_type(dbtype=JSONB, nested=True))
    # properties = Column(mutable_json_type(dbtype=JSONB, nested=True), nullable=True)
    historical_locations = relationship('HistoricalLocation', backref='location')


class HistoricalLocation(Base):
    __tablename__ = 'historical_location'

    id = Column(Integer, primary_key=True)
    time = Column(DateTime)
    location_id = Column(Integer, ForeignKey('location.id'), nullable=True)
    thing_id = Column(Integer, ForeignKey('thing.id'))


class ObservationType(Base):
    __tablename__ = 'observation_type'

    code = Column(String, primary_key=True)
    name = Column(String)


class DataStream(Base):
    __tablename__ = 'data_stream'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    # unit_of_measurement = Column(mutable_json_type(dbtype=JSONB, nested=True))
    observation_type = Column(String, ForeignKey('observation_type.code'))
    # properties = Column(mutable_json_type(dbtype=JSONB, nested=True), nullable=True)
    # observed_area = Column(mutable_json_type(dbtype=JSONB, nested=True), nullable=True)
    phenomenon_time = Column(DateTime, nullable=True)
    result_time = Column(DateTime, nullable=True)
    sensor_id = Column(Integer, ForeignKey('sensor.id'))
    observed_property_id = Column(Integer, ForeignKey('observed_property.id'))


class SensorEncodingType(Base):
    __tablename__ = 'sensor_encoding_type'

    code = Column(String, primary_key=True)
    name = Column(String)


class Sensor(Base):
    __tablename__ = 'sensor'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    encoding_type = Column(String, ForeignKey('sensor_encoding_type.code'))
    sensor_metadata = Column(LargeBinary)
    # properties = Column(mutable_json_type(dbtype=JSONB, nested=True), nullable=True)
    data_streams = relationship('DataStream', backref='sensor')


class ObservedProperty(Base):
    __tablename__ = 'observed_property'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    definition = Column(String)
    description = Column(String)
    # properties = Column(mutable_json_type(dbtype=JSONB, nested=True), nullable=True)
    data_streams = relationship('DataStream', backref='observed_property')


class Observation(Base):
    __tablename__ = 'observation'

    id = Column(Integer, primary_key=True)
    result = Column(String)
    result_time = Column(DateTime)
    result_quality = Column(String, nullable=True)
    valid_time = Column(DateTime, nullable=True)
    # properties = Column(mutable_json_type(dbtype=JSONB, nested=True), nullable=True)
    data_stream_id = Column(Integer, ForeignKey('data_stream.id'))
    feature_of_interest_id = Column(Integer, ForeignKey('feature_of_interest.id'))


class FeatureOfInterest(Base):
    __tablename__ = 'feature_of_interest'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    encoding_type = Column(String, ForeignKey('location_encoding_type.code'))
    # feature = Column(mutable_json_type(dbtype=JSONB, nested=True))
    # properties = Column(mutable_json_type(dbtype=JSONB, nested=True), nullable=True)
    observations = relationship('Observation', backref='feature_of_interest')
