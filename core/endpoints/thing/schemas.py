import pydantic
from ninja import Schema
from pydantic import Field
from typing import List, Optional
from uuid import UUID
from sensorthings.validators import allow_partial
from core.endpoints.observedproperty.schemas import ObservedPropertyGetResponse
from core.endpoints.processinglevel.schemas import ProcessingLevelGetResponse
from core.endpoints.unit.schemas import UnitGetResponse
from core.endpoints.sensor.schemas import SensorGetResponse
from core.endpoints.tags.schemas import TagGetResponse
from core.schemas import BasePostBody, BasePatchBody
from country_list import countries_for_language


class ThingID(Schema):
    id: UUID


class ThingFields(Schema):
    name: str
    description: str
    sampling_feature_type: str = Field(alias='samplingFeatureType')
    sampling_feature_code: str = Field(alias='samplingFeatureCode')
    site_type: str = Field(alias='siteType')
    data_disclaimer: str = Field(None, alias='dataDisclaimer')
    hydroshare_archive_resource_id: str = Field(None, alias='hydroShareArchiveResourceId')


# Get a list of all ISO 3166-1 alpha-2 country codes
valid_country_codes = [code for code, _ in countries_for_language('en')]

class LocationFields(Schema):
    latitude: float
    longitude: float
    elevation_m: float = None
    elevation_datum: str = Field(None, alias='elevationDatum')
    state: str = None
    county: str = None
    country: str = None

    @pydantic.root_validator
    def check_country_code(cls, values):
        country_code = values.get('country')
        if country_code and country_code.upper() not in valid_country_codes:
            raise ValueError(f'Invalid country code: {country_code}. Must be an ISO 3166-1 alpha-2 country code.')
        return values


class OrganizationFields(Schema):
    name: Optional[str] = Field(None, alias='organizationName')


class AssociationFields(Schema):
    is_primary_owner: bool = Field(..., alias='isPrimaryOwner')


class PersonFields(Schema):
    first_name: str = Field(..., alias='firstName')
    last_name: str = Field(..., alias='lastName')
    email: str

    class Config:
        allow_population_by_field_name = True


class OwnerFields(AssociationFields, OrganizationFields, PersonFields):
    pass


class ThingGetResponse(LocationFields, ThingFields, ThingID):
    is_private: bool = Field(..., alias='isPrivate')
    is_primary_owner: bool = Field(..., alias='isPrimaryOwner')
    owns_thing: bool = Field(..., alias='ownsThing')
    follows_thing: bool = Field(..., alias='followsThing')
    owners: List[OwnerFields]
    tags: List[TagGetResponse]

    class Config:
        allow_population_by_field_name = True


class ThingPostBody(BasePostBody, ThingFields, LocationFields):
    pass


@allow_partial
class ThingPatchBody(BasePatchBody, ThingFields, LocationFields):
    pass


class ThingOwnershipPatchBody(Schema):
    email: str
    make_owner: Optional[bool] = Field(False, alias='makeOwner')
    remove_owner: Optional[bool] = Field(False, alias='removeOwner')
    transfer_primary: Optional[bool] = Field(False, alias='transferPrimary')

    @pydantic.root_validator()
    def validate_only_one_method_allowed(cls, field_values):

        assert [
                   field_values.get('make_owner', False),
                   field_values.get('remove_owner', False),
                   field_values.get('transfer_primary', False)
               ].count(True) == 1, \
            'You must perform one and only one action from among "makeOwner", "removeOwner", and "transferPrimary".'

        return field_values


class ThingPrivacyPatchBody(Schema):
    is_private: bool = Field(..., alias="isPrivate")


class ThingMetadataGetResponse(Schema):
    units: List[UnitGetResponse]
    sensors: List[SensorGetResponse]
    processing_levels: List[ProcessingLevelGetResponse] = Field(..., alias='processingLevels')
    observed_properties: List[ObservedPropertyGetResponse] = Field(..., alias='observedProperties')

    class Config:
        allow_population_by_field_name = True


class ThingArchiveBody(Schema):
    resource_title: str = Field(..., alias='resourceTitle')
    resource_abstract: str = Field(..., alias='resourceAbstract')
    resource_keywords: List[str] = Field(None, alias='resourceKeywords')
    public_resource: bool = Field(False, alias='publicResource')
    datastreams: List[UUID] = Field(None, alias='datastreams')
