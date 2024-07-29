from ninja import Schema, Field
from typing import List, Union, Optional
from datetime import datetime
from sensorthings.components.locations.schemas import (LocationGetResponse as DefaultLocationGetResponse,
                                                       LocationListResponse as DefaultLocationListResponse)


class LocationProperties(Schema):
    state: Union[str, None] = None
    county: Union[str, None] = None
    elevation_m: Union[float, None] = None
    elevation_datum: Union[str, None] = Field(None, alias='elevationDatum')
    last_updated: Optional[datetime] = Field(None, alias='lastUpdated')

    class Config:
        populate_by_name = True


class LocationGetResponse(DefaultLocationGetResponse):
    properties: LocationProperties


class LocationListResponse(DefaultLocationListResponse):
    value: List[LocationGetResponse]
