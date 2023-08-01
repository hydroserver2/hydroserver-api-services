from uuid import UUID
from ninja import Schema, Field
from typing import Optional, List
from pydantic import validator


class ThingFields(Schema):
    id: UUID
    name: str
    description: Optional[str]
    sampling_feature_type: Optional[str]
    sampling_feature_code: Optional[str]
    site_type: Optional[str]
    is_private: bool
    latitude: float = Field(..., alias='location__latitude')
    longitude: float = Field(..., alias='location__longitude')
    elevation: float = Field(..., alias='location__elevation')
    state: Optional[str] = Field(..., alias='location__state')
    county: Optional[str] = Field(..., alias='location__county')
    city: Optional[str] = Field(..., alias='location__city')
    is_primary_owner: bool = False
    owns_thing: bool = False
    follows_thing: bool = False
    owners: List[dict] = []

    @validator('latitude', 'longitude', 'elevation')
    def round_floats(cls, value):
        return round(value, 6)


class ThingQueryParams(Schema):
    pass


class ThingGetResponse(ThingFields):
    pass


class ThingPostBody(ThingFields):
    pass


class ThingPatchBody(ThingFields):
    pass
