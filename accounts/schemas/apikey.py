from ninja import Schema
from datetime import datetime
from typing import Optional, Literal, List
from uuid import UUID
from hydroserver.schemas import BaseGetResponse, BasePostBody, BasePatchBody


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
    resources: Optional[List[APIKeyResource]] = None
    fields: Optional[List[str]] = None


class APIKeyFields(Schema):
    name: str
    permissions: Optional[List[APIKeyPermissions]] = None
    expires: Optional[datetime] = None
    enabled: bool
    last_used: Optional[datetime] = None


class APIKeyGetResponse(BaseGetResponse, APIKeyFields):
    id: UUID


class APIKeyPostBody(BasePostBody, APIKeyFields):
    pass


class APIKeyPatchBody(BasePatchBody, APIKeyFields):
    pass


class APIKeyPostResponse(APIKeyGetResponse):
    key: str
