from typing import List
from uuid import UUID
from sensorthings import SensorThingsAbstractEngine


class HydroServerSensorThingsEngine(SensorThingsAbstractEngine):








    def get_datastreams(
            self,
            datastream_ids: List[UUID] = None,
            observed_property_ids: List[UUID] = None,
            sensor_ids: List[UUID] = None,
            thing_ids: List[UUID] = None,
            pagination: dict = None,
            ordering: dict = None,
            filters: dict = None
    ) -> List[dict]:

        return []

    def create_datastream(
            self,
            datastream
    ) -> UUID:
        pass

    def update_datastream(
            self,
            datastream_id: UUID,
            datastream
    ) -> None:
        pass

    def delete_datastream(
            self,
            datastream_id: UUID
    ) -> None:
        pass


HydroServerSensorThingsEngine()
