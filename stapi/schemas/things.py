from ninja import Schema, Field
from pydantic import ConfigDict
from typing import List, Optional
from datetime import datetime
from sensorthings.components.things.schemas import (ThingGetResponse as DefaultThingGetResponse,
                                                    ThingListResponse as DefaultThingListResponse)


class ContactPerson(Schema):
    model_config = ConfigDict(populate_by_name=True)

    first_name: str = Field(..., alias='firstName')
    last_name: str = Field(..., alias='lastName')
    email: str = Field(..., alias='email')
    organization_name: Optional[str] = Field(None, alias='organizationName')


class ThingProperties(Schema):
    model_config = ConfigDict(populate_by_name=True)

    sampling_feature_type: str = Field(..., alias='samplingFeatureType')
    sampling_feature_code: str = Field(..., alias='samplingFeatureCode')
    site_type: str = Field(..., alias='siteType')
    contact_people: List[ContactPerson] = Field(..., alias='contactPeople')
    last_updated: Optional[datetime] = Field(None, alias='lastUpdated')


class ThingGetResponse(DefaultThingGetResponse):
    model_config = ConfigDict(populate_by_name=True)

    properties: ThingProperties


class ThingListResponse(DefaultThingListResponse):
    value: List[ThingGetResponse]
