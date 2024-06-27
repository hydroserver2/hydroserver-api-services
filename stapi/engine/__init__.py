from sensorthings import SensorThingsBaseEngine
from stapi.engine.components import DatastreamEngine, FeatureOfInterestEngine, HistoricalLocationEngine, \
     LocationEngine, ObservationEngine, ObservedPropertyEngine, SensorEngine, ThingEngine


class HydroServerSensorThingsEngine(
    DatastreamEngine,
    FeatureOfInterestEngine,
    HistoricalLocationEngine,
    LocationEngine,
    ObservationEngine,
    ObservedPropertyEngine,
    SensorEngine,
    ThingEngine,
    SensorThingsBaseEngine
):
    pass
