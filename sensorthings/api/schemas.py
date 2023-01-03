from pydantic import Field
from ninja import Schema


class Filters(Schema):
    filter: str = Field(None, alias='$filter')
    count: str = Field(None, alias='$count')
    orderby: str = Field(None, alias='$orderby')
    skip: str = Field(None, alias='$skip')
    top: str = Field(None, alias='$top')
    select: str = Field(None, alias='$select')
    expand: str = Field(None, alias='$expand')
