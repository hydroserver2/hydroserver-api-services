from ninja import Schema, Field
from pydantic import AnyUrl
from sensorthings.core import components as core_components


class ObservedPropertyProperties(Schema):
    variable_type: str = Field(..., alias='variableType')
    variable_code: str = Field(..., alias='variableCode')


class ObservedPropertyGetResponse(core_components.ObservedPropertyGetResponse):
    properties: ObservedPropertyProperties
