from ninja import Schema, Field
from pydantic import ConfigDict
from pydantic.alias_generators import to_camel
from typing import Optional
from sensorthings.components.locations.schemas import (
    LocationGetResponse as DefaultLocationGetResponse,
    LocationListResponse as DefaultLocationListResponse,
)
from .workspace import WorkspaceProperties


class LocationProperties(Schema):
    state: Optional[str] = None
    county: Optional[str] = None
    elevation_m: Optional[float] = Field(None, alias="elevation_m")
    elevation_datum: Optional[str] = None
    workspace: WorkspaceProperties

    model_config = ConfigDict(
        populate_by_name=True, str_strip_whitespace=True, alias_generator=to_camel
    )


class LocationGetResponse(DefaultLocationGetResponse):
    properties: LocationProperties


class LocationListResponse(DefaultLocationListResponse):
    value: list[LocationGetResponse]
