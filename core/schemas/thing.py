import pydantic
from ninja import Schema
from pydantic import Field
from typing import List, Optional, Literal
from uuid import UUID
from sensorthings.validators import allow_partial
from core.schemas.observed_property import ObservedPropertyGetResponse
from core.schemas.processing_level import ProcessingLevelGetResponse
from core.schemas.unit import UnitGetResponse
from core.schemas.sensor import SensorGetResponse
from core.schemas import BasePostBody, BasePatchBody
from country_list import countries_for_language


class ArchiveFields(Schema):
    link: Optional[str] = Field(None, alias='link')
    frequency: Optional[Literal['daily', 'weekly', 'monthly']]
    path: str = Field(..., alias='path')
    datastream_ids: List[UUID] = Field(..., alias='datastreamIds')


class ArchiveGetResponse(ArchiveFields):
    thing_id: UUID = Field(..., alias='thingId')
    public_resource: bool = Field(..., alias='publicResource')

    @classmethod
    def serialize(cls, archive):  # Temporary until after Pydantic v2 update
        return {
            **{field: getattr(archive, field) for field in cls.__fields__.keys()}
        }

    class Config:
        allow_population_by_field_name = True


class ArchivePostBody(ArchiveFields):
    resource_title: Optional[str] = Field(None, alias='resourceTitle')
    resource_abstract: Optional[str] = Field(None, alias='resourceAbstract')
    resource_keywords: Optional[List[str]] = Field(None, alias='resourceKeywords')
    public_resource: Optional[bool] = Field(None, alias='publicResource')


@allow_partial
class ArchivePatchBody(ArchiveFields):
    pass


class TagID(Schema):
    id: UUID


class TagFields(Schema):
    key: str
    value: str


class TagGetResponse(TagFields, TagID):
    @classmethod
    def serialize(cls, tag):  # Temporary until after Pydantic v2 update
        return {
            'id': tag.id,
            'key': tag.key,
            'value': tag.value
        }

    class Config:
        allow_population_by_field_name = True


class TagPostBody(TagFields):
    pass


@allow_partial
class TagPatchBody(TagFields):
    pass


class PhotoID(Schema):
    id: UUID


class PhotoFields(Schema):
    thing_id: UUID = Field(..., alias='thingId')
    file_path: str = Field(..., alias='filePath')
    link: str


class PhotoGetResponse(PhotoFields, PhotoID):
    @classmethod
    def serialize(cls, photo):  # Temporary until after Pydantic v2 update
        return {
            'id': photo.id,
            'thing_id': photo.thing_id,
            'file_path': str(photo.file_path),
            'link': photo.link
        }

    class Config:
        allow_population_by_field_name = True


class ThingID(Schema):
    id: UUID


class ThingFields(Schema):
    name: str
    description: str
    sampling_feature_type: str = Field(alias='samplingFeatureType')
    sampling_feature_code: str = Field(alias='samplingFeatureCode')
    site_type: str = Field(alias='siteType')
    data_disclaimer: str = Field(None, alias='dataDisclaimer')


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
    owners: List[OwnerFields]
    tags: List[TagGetResponse]

    @classmethod
    def serialize(cls, thing, user):  # Temporary until after Pydantic v2 update
        thing_association = next(iter([
            associate for associate in thing.associates.all() if user and associate.person.id == user.id
        ]), None)

        return {
            'id': thing.id,
            'is_private': thing.is_private,
            'is_primary_owner': getattr(thing_association, 'is_primary_owner', False),
            'owns_thing': getattr(thing_association, 'owns_thing', False),
            'tags': [
                {'id': tag.id, 'key': tag.key, 'value': tag.value} for tag in thing.tags.all()
            ],
            'owners': [{
                **{field: getattr(associate, field) for field in AssociationFields.__fields__.keys()},
                **{field: getattr(associate.person, field) for field in PersonFields.__fields__.keys()},
                **{field: getattr(associate.person.organization, field, None)
                   for field in OrganizationFields.__fields__.keys()},
            } for associate in thing.associates.all() if associate.owns_thing is True and associate.person.is_active],
            **{field: getattr(thing, field) for field in ThingFields.__fields__.keys()},
            **{field: getattr(thing.location, field) for field in LocationFields.__fields__.keys()}
        }

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
