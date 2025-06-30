import uuid
from ninja import Query
from pydantic import EmailStr
from hydroserver.schemas import BaseGetResponse, BasePostBody, CollectionQueryParameters
from .role import RoleGetResponse
from .account import AccountContactGetResponse


class CollaboratorQueryParameters(CollectionQueryParameters):
    role_id: list[uuid.UUID] = Query(
        [], description="Filter collaborators by role ID."
    )


class CollaboratorGetResponse(BaseGetResponse):
    user: AccountContactGetResponse
    role: RoleGetResponse


class CollaboratorPostBody(BasePostBody):
    email: EmailStr
    role_id: uuid.UUID


class CollaboratorDeleteBody(BasePostBody):
    email: EmailStr
