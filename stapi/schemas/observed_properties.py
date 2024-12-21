from uuid import UUID
from ninja import Schema, Field
from pydantic import ConfigDict
from typing import List, Union, Optional
from datetime import datetime
from sensorthings.types import ISOTimeString, ISOIntervalString
from sensorthings.components.observedproperties.schemas import (ObservedPropertyGetResponse as
                                                                DefaultObservedPropertyGetResponse,
                                                                ObservedPropertyListResponse as
                                                                DefaultObservedPropertyListResponse)


class ObservedPropertyProperties(Schema):
    model_config = ConfigDict(populate_by_name=True)

    variable_code: str = Field(..., alias='variableCode')
    variable_type: str = Field(..., alias='variableType')
    last_updated: Optional[datetime] = Field(None, alias='lastUpdated')


class ObservedPropertyGetResponse(DefaultObservedPropertyGetResponse):
    definition: str
    properties: ObservedPropertyProperties


class ObservedPropertyListResponse(DefaultObservedPropertyListResponse):
    value: List[ObservedPropertyGetResponse]
