from typing import TYPE_CHECKING, Literal
from pydantic import BaseModel

if TYPE_CHECKING:
    from ..things.models import Thing


locationEncodingTypes = Literal['application/geo+json']


class LocationProps(BaseModel):
    name: str
    description: str
    encodingType: locationEncodingTypes
    location: dict
    properties: dict = {}


class LocationRelations(BaseModel):
    thing: 'list[Thing]' = []


class Location(LocationProps, LocationRelations):
    pass
