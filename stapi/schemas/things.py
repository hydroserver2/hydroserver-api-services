from ninja import Schema, Field
from typing import List, Optional
from datetime import datetime
from sensorthings.components.things.schemas import (ThingGetResponse as DefaultThingGetResponse,
                                                    ThingListResponse as DefaultThingListResponse)


class ContactPerson(Schema):
    first_name: str = Field(..., alias='firstName')
    last_name: str = Field(..., alias='lastName')
    email: str = Field(..., alias='email')
    organization_name: Optional[str] = Field(None, alias='organizationName')

    class Config:
        populate_by_name = True


class ThingProperties(Schema):
    sampling_feature_type: str = Field(..., alias='samplingFeatureType')
    sampling_feature_code: str = Field(..., alias='samplingFeatureCode')
    site_type: str = Field(..., alias='siteType')
    contact_people: List[ContactPerson] = Field(..., alias='contactPeople')
    last_updated: Optional[datetime] = Field(None, alias='lastUpdated')

    class Config:
        populate_by_name = True


class ThingGetResponse(DefaultThingGetResponse):
    properties: ThingProperties

    class Config:
        populate_by_name = True


class ThingListResponse(DefaultThingListResponse):
    value: List[ThingGetResponse]
