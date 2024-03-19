from ninja import Schema
from datetime import datetime
from typing import Optional, Literal, List
from uuid import UUID
from sensorthings.validators import allow_partial


permissions_methods = Literal['GET', 'POST', 'PATCH', 'DELETE']
permissions_models = Literal[
    'Thing', 'Photo', 'Tag', 'Datastream', 'ObservedProperty', 'ProcessingLevel', 'Sensor', 'Unit', 'ResultQualifier',
    'DataLoader', 'DataSource', 'Observation'
]


class APIKeyPermissions(Schema):
    model: permissions_models
    methods: List[permissions_methods]
    resources: List[str]
    fields: List[str]


class APIKeyFields(Schema):
    name: str
    scope: str
    permissions: Optional[dict]
    expires: Optional[datetime]


class APIKeyGetResponse(APIKeyFields):
    id: UUID


class APIKeyPostBody(APIKeyFields):
    pass


@allow_partial
class APIKeyPatchBody(APIKeyFields):
    pass


class APIKeyPostResponse(APIKeyGetResponse):
    key: str
