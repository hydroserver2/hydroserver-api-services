from typing import TYPE_CHECKING
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from ..locations.models import Location


class ThingProps(BaseModel):
    name: str
    description: str
    properties: dict = {}


class ThingRelations(BaseModel):
    location: 'list[Location]' = []


class Thing(ThingProps, ThingRelations):
    pass
