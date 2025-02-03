import uuid
from pydantic import EmailStr
from hydroserver.schemas import BasePostBody


class CollaboratorPostBody(BasePostBody):
    email: EmailStr
    role_id: uuid.UUID
