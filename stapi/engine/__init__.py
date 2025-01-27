from sensorthings import SensorThingsBaseEngine
from sensorthings.extensions.dataarray.engine import DataArrayBaseEngine
from sensorthings.extensions.qualitycontrol.engine import QualityControlBaseEngine
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
    DataArrayBaseEngine,
    QualityControlBaseEngine
):
    pass
