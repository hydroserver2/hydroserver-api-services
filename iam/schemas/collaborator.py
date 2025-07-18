import uuid
from typing import TYPE_CHECKING
from ninja import Query
from pydantic import EmailStr
from api.schemas import BaseGetResponse, BasePostBody, CollectionQueryParameters

if TYPE_CHECKING:
    from iam.schemas import AccountContactDetailResponse, RoleSummaryResponse


class CollaboratorQueryParameters(CollectionQueryParameters):
    role_id: list[uuid.UUID] = Query([], description="Filter collaborators by role ID.")


class CollaboratorDetailResponse(BaseGetResponse):
    user: "AccountContactDetailResponse"
    role: "RoleSummaryResponse"


class CollaboratorPostBody(BasePostBody):
    email: EmailStr
    role_id: uuid.UUID


class CollaboratorDeleteBody(BasePostBody):
    email: EmailStr
