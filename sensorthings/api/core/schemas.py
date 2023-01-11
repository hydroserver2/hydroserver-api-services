from pydantic import Field, Extra, HttpUrl, validator
from ninja import Schema
from sensorthings.api.core.utils import whitespace_to_none


class BasePostBody(Schema):

    class Config:
        extra = Extra.forbid


class BasePatchBody(Schema):

    _whitespace_validator = validator('*', allow_reuse=True, check_fields=False, pre=True)(whitespace_to_none)

    class Config:
        extra = Extra.forbid


class BaseListResponse(Schema):
    count: int = Field(..., alias='@iot.count')
    value: list = []
    next_link: HttpUrl = Field(None, alias='@iot.nextLink')


class BaseGetResponse(Schema):
    id: int = Field(..., alias='@iot.id')
    self_link: HttpUrl = Field(..., alias='@iot.selfLink')


class Filters(Schema):
    filter: str = Field(None, alias='$filter')
    count: str = Field(None, alias='$count')
    order_by: str = Field(None, alias='$orderby')
    skip: str = Field(None, alias='$skip')
    top: str = Field(None, alias='$top')
    select: str = Field(None, alias='$select')
    expand: str = Field(None, alias='$expand')
    result_format: str = Field(None, alias='$resultFormat')
