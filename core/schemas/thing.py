from ninja import Schema, Field
from pydantic import AliasPath, AliasChoices, model_validator, field_validator
from typing import List, Optional, Literal
from uuid import UUID
from core.schemas.observed_property import ObservedPropertyGetResponse
from core.schemas.processing_level import ProcessingLevelGetResponse
from core.schemas.unit import UnitGetResponse
from core.schemas.sensor import SensorGetResponse
from hydroserver.schemas import BaseGetResponse, BasePostBody, BasePatchBody
from country_list import countries_for_language


class ArchiveFields(Schema):
    link: Optional[str] = None
    frequency: Optional[Literal['daily', 'weekly', 'monthly']]
    path: str
    datastream_ids: List[UUID]


class ArchiveGetResponse(BaseGetResponse, ArchiveFields):
    thing_id: UUID
    public_resource: bool

    class Config:
        allow_population_by_field_name = True


class ArchivePostBody(BasePostBody, ArchiveFields):
    resource_title: Optional[str] = None
    resource_abstract: Optional[str] = None
    resource_keywords: Optional[List[str]] = None
    public_resource: Optional[bool] = None


class ArchivePatchBody(BasePatchBody, ArchiveFields):
    pass


class TagID(Schema):
    id: UUID


class TagFields(Schema):
    key: str
    value: str


class TagGetResponse(BaseGetResponse, TagFields, TagID):

    class Config:
        allow_population_by_field_name = True


class TagPostBody(BasePostBody, TagFields):
    pass


class TagPatchBody(BasePatchBody, TagFields):
    pass


class PhotoID(Schema):
    id: UUID


class PhotoFields(Schema):
    thing_id: UUID
    file_path: str
    link: str


class PhotoGetResponse(BaseGetResponse, PhotoFields, PhotoID):

    class Config:
        allow_population_by_field_name = True


class ThingID(Schema):
    id: UUID


class ThingFields(Schema):
    name: str
    description: str
    sampling_feature_type: str
    sampling_feature_code: str
    site_type: str
    data_disclaimer: Optional[str] = None


# Get a list of all ISO 3166-1 alpha-2 country codes
valid_country_codes = [code for code, _ in countries_for_language('en')]


class LocationFields(Schema):
    latitude: float = Field(
        ..., serialization_alias='latitude',
        validation_alias=AliasChoices('latitude', AliasPath('location', 'latitude'))
    )
    longitude: float = Field(
        ..., serialization_alias='longitude',
        validation_alias=AliasChoices('longitude', AliasPath('location', 'longitude'))
    )
    elevation_m: Optional[float] = Field(
        None, serialization_alias='elevation_m',
        validation_alias=AliasChoices('elevation_m', AliasPath('location', 'elevation_m'))
    )
    elevation_datum: Optional[str] = Field(
        None, serialization_alias='elevationDatum',
        validation_alias=AliasChoices('elevationDatum', AliasPath('location', 'elevationDatum'))
    )
    state: Optional[str] = Field(
        None, serialization_alias='state',
        validation_alias=AliasChoices('state', AliasPath('location', 'state'))
    )
    county: Optional[str] = Field(
        None, serialization_alias='county',
        validation_alias=AliasChoices('county', AliasPath('location', 'county'))
    )
    country: Optional[str] = Field(
        None, serialization_alias='country',
        validation_alias=AliasChoices('country', AliasPath('location', 'country'))
    )

    @field_validator('country', mode='after')
    def check_country_code(cls, value):
        if value and value.upper() not in valid_country_codes:
            raise ValueError(f'Invalid country code: {value}. Must be an ISO 3166-1 alpha-2 country code.')
        return value


class OwnerFields(Schema):
    first_name: str = Field(
        ..., serialization_alias='firstName',
        validation_alias=AliasChoices('firstName', AliasPath('person', 'first_name'))
    )
    last_name: str = Field(
        ..., serialization_alias='lastName',
        validation_alias=AliasChoices('lastName', AliasPath('person', 'first_name'))
    )
    email: str = Field(
        ..., serialization_alias='email',
        validation_alias=AliasChoices('email', AliasPath('person', 'first_name'))
    )
    organization_name: Optional[str] = Field(
        None, serialization_alias='organizationName',
        validation_alias=AliasChoices('organizationName', AliasPath('person', 'organization', 'name'))
    )
    is_primary_owner: bool = Field(
        ..., serialization_alias='isPrimaryOwner',
        validation_alias=AliasChoices('isPrimaryOwner', 'is_primary_owner')
    )

    class Config:
        allow_population_by_field_name = True


class OwnerGetResponse(BaseGetResponse, OwnerFields):
    pass


class ThingGetResponse(BaseGetResponse, LocationFields, ThingFields, ThingID):
    is_private: bool
    is_primary_owner: bool
    owns_thing: bool
    owners: List[OwnerGetResponse]
    tags: List[TagGetResponse]

    class Config:
        allow_population_by_field_name = True


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
    units: List[UnitGetResponse]
    sensors: List[SensorGetResponse]
    processing_levels: List[ProcessingLevelGetResponse]
    observed_properties: List[ObservedPropertyGetResponse]

    class Config:
        allow_population_by_field_name = True


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
