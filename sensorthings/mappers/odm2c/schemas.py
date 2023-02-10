from ninja import Schema, Field
from pydantic import AnyUrl
from sensorthings.core import components as core_components


class People(Schema):
    id: int = Field(..., alias='personID')
    first_name: str = Field(..., alias='personFirstName')
    middle_name: str = Field(..., alias='personMiddleName')
    last_name: str = Field(..., alias='personLastName')
    phone: str | None = None
    email: str
    address: str | None = None
    link: AnyUrl | None = None


class Organization(Schema):
    id: int = Field(..., alias='organizationID')
    code: str = Field(..., alias='organizationCode')
    name: str = Field(..., alias='organizationName')
    description: str | None = Field(None, alias='organizationDescription')
    type: str = Field(..., alias='organizationType')
    link: AnyUrl | None = Field(..., alias='organizationLink')


class ThingProperties(Schema):
    sampling_feature_type: str = Field(..., alias='samplingFeatureType')
    sampling_feature_code: str = Field(..., alias='samplingFeatureCode')
    site_type: str = Field(..., alias='siteType')
    state: str
    county: str
    contact_person: People = Field(..., alias='contactPerson')
    responsible_organization: Organization = Field(..., alias='responsibleOrganization')


class ThingGetResponse(core_components.ThingGetResponse):
    properties: ThingProperties
