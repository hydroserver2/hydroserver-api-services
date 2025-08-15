from ninja import Schema, Field
from typing import Literal, Optional
from uuid import UUID
from api.schemas import BaseGetResponse, BasePostBody, BasePatchBody


class HydroShareArchivalFields(Schema):
    link: Optional[str] = None
    frequency: Optional[Literal["daily", "weekly", "monthly"]] = None
    path: str = Field(..., max_length=255)
    datastream_ids: list[UUID]


class HydroShareArchivalDetailResponse(BaseGetResponse, HydroShareArchivalFields):
    thing_id: Optional[UUID]


class HydroShareArchivalPostBody(BasePostBody, HydroShareArchivalFields):
    resource_title: Optional[str] = Field(None, max_length=255)
    resource_abstract: Optional[str] = None
    resource_keywords: Optional[list[str]] = None
    public_resource: bool = False


class HydroShareArchivalPatchBody(BasePatchBody, HydroShareArchivalFields):
    pass
