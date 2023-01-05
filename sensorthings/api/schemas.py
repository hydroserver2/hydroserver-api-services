from pydantic import Field, HttpUrl
from ninja import Schema


class Filters(Schema):
    filter: str = Field(None, alias='$filter')
    count: str = Field(None, alias='$count')
    order_by: str = Field(None, alias='$orderby')
    skip: str = Field(None, alias='$skip')
    top: str = Field(None, alias='$top')
    select: str = Field(None, alias='$select')
    expand: str = Field(None, alias='$expand')
    result_format: str = Field(None, alias='$resultFormat')


class BaseEntitiesResponse(Schema):
    count: int = Field(..., alias='@iot.count')
    value: list = []
    next_link: HttpUrl = Field(None, alias='@iot.nextLink')


class BaseEntityResponse(Schema):
    id: int = Field(..., alias='@iot.id')
    self_link: HttpUrl = Field(..., alias='@iot.selfLink')


class DataArrayResponse(Schema):
    components: list
    dataArray: list
