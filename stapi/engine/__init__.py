from sensorthings import SensorThingsBaseEngine
from sensorthings.extensions import DataArrayBaseEngine
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
    SensorThingsBaseEngine,
    DataArrayBaseEngine
):
    pass
