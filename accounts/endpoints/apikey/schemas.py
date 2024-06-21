from ninja import Schema
from datetime import datetime
from typing import Optional, Literal, List
from pydantic import Field
from uuid import UUID
# from sensorthings.validators import disable_required_field_validation


permissions_methods = Literal['GET', 'POST', 'PATCH', 'DELETE']
permissions_models = Literal[
    'Thing', 'Datastream', 'ObservedProperty', 'ProcessingLevel', 'Sensor', 'Unit', 'ResultQualifier',
    'DataLoader', 'DataSource', 'Observation'
]


class APIKeyResource(Schema):
    model: permissions_models
    ids: List[UUID]


class APIKeyPermissions(Schema):
    model: permissions_models
    methods: List[permissions_methods]
    resources: Optional[List[APIKeyResource]]
    fields: Optional[List[str]]


class APIKeyFields(Schema):
    name: str
    scope: str
    permissions: Optional[List[APIKeyPermissions]]
    expires: Optional[datetime]
    enabled: bool
    last_used: Optional[datetime] = Field(default=None, alias='lastUsed')


class APIKeyGetResponse(APIKeyFields):
    id: UUID


class APIKeyPostBody(APIKeyFields):
    pass


# @disable_required_field_validation
class APIKeyPatchBody(APIKeyFields):
    pass


class APIKeyPostResponse(APIKeyGetResponse):
    key: str
