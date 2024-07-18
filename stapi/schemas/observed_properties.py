from uuid import UUID
from ninja import Schema, Field
from typing import List, Union, Optional
from datetime import datetime
from sensorthings.types import ISOTimeString, ISOIntervalString
from sensorthings.components.observedproperties.schemas import (ObservedPropertyGetResponse as
                                                                DefaultObservedPropertyGetResponse,
                                                                ObservedPropertyListResponse as
                                                                DefaultObservedPropertyListResponse)


class ObservedPropertyProperties(Schema):
    variable_code: str = Field(..., alias='variableCode')
    variable_type: str = Field(..., alias='variableType')
    last_updated: Optional[datetime] = Field(None, alias='lastUpdated')

    class Config:
        populate_by_name = True


class ObservedPropertyGetResponse(DefaultObservedPropertyGetResponse):
    definition: str
    properties: ObservedPropertyProperties


class ObservedPropertyListResponse(DefaultObservedPropertyListResponse):
    value: List[ObservedPropertyGetResponse]
