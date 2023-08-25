from uuid import UUID
from ninja import Schema, Field
from typing import Optional, List
from pydantic import validator, root_validator, AnyHttpUrl
from sensorthings.validators import allow_partial


class ThingOwner(Schema):
    firstname: str = Field(..., alias='person__first_name')
    lastname: str = Field(..., alias='person__last_name')
    organization: Optional[str] = Field(None, alias='person__organization')
    email: Optional[str] = Field(None, alias='person__email')
    is_primary_owner: bool = False


class ThingPhoto(Schema):
    id: UUID
    thing_id: UUID = Field(..., alias='thingId')
    url: AnyHttpUrl


class ThingFields(Schema):
    name: str
    description: Optional[str]
    sampling_feature_type: Optional[str]
    sampling_feature_code: Optional[str]
    site_type: Optional[str]
    latitude: float = Field(..., alias='location__latitude')
    longitude: float = Field(..., alias='location__longitude')
    elevation: float = Field(..., alias='location__elevation')
    state: Optional[str] = Field(..., alias='location__state')
    county: Optional[str] = Field(..., alias='location__county')
    city: Optional[str] = Field(..., alias='location__city')

    @validator('latitude', 'longitude', 'elevation', allow_reuse=True)
    def round_floats(cls, value):
        return round(value, 6)


class ThingQueryParams(Schema):
    pass


class ThingGetResponse(ThingFields):
    id: UUID
    is_private: bool
    is_primary_owner: bool = False
    owns_thing: bool = False
    follows_thing: bool = False
    owners: List[ThingOwner] = []


class ThingPostBody(ThingFields):
    pass


@allow_partial
class ThingPatchBody(ThingFields):
    pass


class ThingPhotoPostBody(Schema):
    photosToDelete: List[UUID]


class ThingOwnershipPatchBody(Schema):
    make_owner: bool
    remove_owner: bool
    transfer_primary: bool
    email: str

    @root_validator(allow_reuse=True)
    def check_only_one_flag(cls, values):
        flags = [values.make_owner, values.remove_owner, values.transfer_primary]
        assert sum(flag is True for flag in flags) == 1, \
            'Only one action (make_owner, remove_owner, transfer_primary) should be true.'

        return values


class ThingPrivacyPatchBody(Schema):
    is_private: bool
