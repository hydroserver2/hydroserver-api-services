from ninja import Schema, Field
from pydantic import ConfigDict, AliasPath, AliasChoices, model_validator, field_validator, StringConstraints as StrCon
from typing import List, Optional, Literal, Annotated
from uuid import UUID
from core.schemas.observed_property import ObservedPropertyGetResponse
from core.schemas.processing_level import ProcessingLevelGetResponse
from core.schemas.unit import UnitGetResponse
from core.schemas.sensor import SensorGetResponse
from hydroserver.schemas import BaseGetResponse, BasePostBody, BasePatchBody
from country_list import countries_for_language


class ArchiveFields(Schema):
    link: Optional[Annotated[str, StrCon(strip_whitespace=True, max_length=255)]] = None
    frequency: Optional[Literal['daily', 'weekly', 'monthly']]
    path: Annotated[str, StrCon(strip_whitespace=True, max_length=255)]
    datastream_ids: List[UUID]


class ArchiveGetResponse(BaseGetResponse, ArchiveFields):
    model_config = ConfigDict(populate_by_name=True)

    thing_id: UUID
    public_resource: bool


class ArchivePostBody(BasePostBody, ArchiveFields):
    resource_title: Optional[Annotated[str, StrCon(strip_whitespace=True, max_length=255)]] = None
    resource_abstract: Optional[Annotated[str, StrCon(strip_whitespace=True)]] = None
    resource_keywords: Optional[List[Annotated[str, StrCon(strip_whitespace=True, max_length=255)]]] = None
    public_resource: Optional[bool] = None


class ArchivePatchBody(BasePatchBody, ArchiveFields):
    pass


class TagID(Schema):
    id: UUID


class TagFields(Schema):
    key: Annotated[str, StrCon(strip_whitespace=True, max_length=255)]
    value: Annotated[str, StrCon(strip_whitespace=True, max_length=255)]


class TagGetResponse(BaseGetResponse, TagFields, TagID):
    model_config = ConfigDict(populate_by_name=True)


class TagPostBody(BasePostBody, TagFields):
    pass


class TagPatchBody(BasePatchBody, TagFields):
    pass


class PhotoID(Schema):
    id: UUID


class PhotoFields(Schema):
    thing_id: UUID
    file_path: Annotated[str, StrCon(strip_whitespace=True)]
    link: Annotated[str, StrCon(strip_whitespace=True)]


class PhotoGetResponse(BaseGetResponse, PhotoFields, PhotoID):
    model_config = ConfigDict(populate_by_name=True)


class ThingID(Schema):
    id: UUID


class ThingFields(Schema):
    name: Annotated[str, StrCon(strip_whitespace=True, max_length=200)]
    description: Annotated[str, StrCon(strip_whitespace=True)]
    sampling_feature_type: Annotated[str, StrCon(strip_whitespace=True, max_length=200)]
    sampling_feature_code: Annotated[str, StrCon(strip_whitespace=True, max_length=200)]
    site_type: Annotated[str, StrCon(strip_whitespace=True, max_length=200)]
    data_disclaimer: Optional[Annotated[str, StrCon(strip_whitespace=True)]] = None


# Get a list of all ISO 3166-1 alpha-2 country codes
valid_country_codes = [code for code, _ in countries_for_language('en')]


class LocationFields(Schema):
    latitude: float = Field(
        ..., ge=-90, le=90, serialization_alias='latitude',
        validation_alias=AliasChoices('latitude', AliasPath('location', 'latitude'))
    )
    longitude: float = Field(
        ..., ge=-180, le=180, serialization_alias='longitude',
        validation_alias=AliasChoices('longitude', AliasPath('location', 'longitude'))
    )
    elevation_m: Optional[float] = Field(
        None, ge=-99999, le=99999, serialization_alias='elevation_m',
        validation_alias=AliasChoices('elevation_m', AliasPath('location', 'elevation_m'))
    )
    elevation_datum: Optional[Annotated[str, StrCon(strip_whitespace=True, max_length=255)]] = Field(
        None, serialization_alias='elevationDatum',
        validation_alias=AliasChoices('elevationDatum', AliasPath('location', 'elevationDatum'))
    )
    state: Optional[Annotated[str, StrCon(strip_whitespace=True, max_length=200)]] = Field(
        None, serialization_alias='state',
        validation_alias=AliasChoices('state', AliasPath('location', 'state'))
    )
    county: Optional[Annotated[str, StrCon(strip_whitespace=True, max_length=200)]] = Field(
        None, serialization_alias='county',
        validation_alias=AliasChoices('county', AliasPath('location', 'county'))
    )
    country: Optional[Annotated[str, StrCon(strip_whitespace=True, max_length=2)]] = Field(
        None, serialization_alias='country',
        validation_alias=AliasChoices('country', AliasPath('location', 'country'))
    )

    @field_validator('country', mode='after')
    def check_country_code(cls, value):
        if value and value.upper() not in valid_country_codes:
            raise ValueError(f'Invalid country code: {value}. Must be an ISO 3166-1 alpha-2 country code.')
        return value


class OwnerFields(Schema):
    model_config = ConfigDict(populate_by_name=True)

    first_name: str = Field(
        ..., serialization_alias='firstName',
        validation_alias=AliasChoices('firstName', AliasPath('person', 'first_name'))
    )
    last_name: str = Field(
        ..., serialization_alias='lastName',
        validation_alias=AliasChoices('lastName', AliasPath('person', 'last_name'))
    )
    email: str = Field(
        ..., serialization_alias='email',
        validation_alias=AliasChoices('email', AliasPath('person', 'email'))
    )
    organization_name: Optional[str] = Field(
        None, serialization_alias='organizationName',
        validation_alias=AliasChoices('organizationName', AliasPath('person', 'organization', 'name'))
    )
    is_primary_owner: bool = Field(
        ..., serialization_alias='isPrimaryOwner',
        validation_alias=AliasChoices('isPrimaryOwner', 'is_primary_owner')
    )


class OwnerGetResponse(BaseGetResponse, OwnerFields):
    pass


class ThingGetResponse(BaseGetResponse, LocationFields, ThingFields, ThingID):
    model_config = ConfigDict(populate_by_name=True)

    is_private: bool
    is_primary_owner: bool
    owns_thing: bool
    owners: List[OwnerGetResponse]
    tags: List[TagGetResponse]


class ThingPostBody(BasePostBody, ThingFields, LocationFields):
    pass


class ThingPatchBody(BasePatchBody, ThingFields, LocationFields):
    pass


class ThingOwnershipPatchBody(BasePatchBody):
    email: str
    make_owner: Optional[bool] = False
    remove_owner: Optional[bool] = False
    transfer_primary: Optional[bool] = False

    @model_validator(mode='after')
    def validate_only_one_method_allowed(self):
        assert [
            self.make_owner,
            self.remove_owner,
            self.transfer_primary
        ].count(True) == 1, \
            'You must perform one and only one action from among "makeOwner", "removeOwner", and "transferPrimary".'

        return self


class ThingPrivacyPatchBody(BasePatchBody):
    is_private: bool


class ThingMetadataGetResponse(BaseGetResponse):
    model_config = ConfigDict(populate_by_name=True)

    units: List[UnitGetResponse]
    sensors: List[SensorGetResponse]
    processing_levels: List[ProcessingLevelGetResponse]
    observed_properties: List[ObservedPropertyGetResponse]


class ThingArchiveFields(Schema):
    resource_title: str
    resource_abstract: str
    resource_keywords: Optional[List[str]] = None
    public_resource: bool = False
    datastreams: Optional[List[UUID]] = None


class ThingArchivePostBody(BasePostBody, ThingArchiveFields):
    pass


class ThingArchivePatchBody(BasePatchBody, ThingArchiveFields):
    pass
