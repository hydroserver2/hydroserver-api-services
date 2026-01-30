from typing import Optional
from interfaces.api.schemas import BaseGetResponse, BasePostBody


class TagGetResponse(BaseGetResponse):
    key: str
    value: str


class TagPostBody(BasePostBody):
    key: str
    value: str


class TagDeleteBody(BasePostBody):
    key: str
    value: Optional[str] = None


class FileAttachmentGetResponse(BaseGetResponse):
    name: str
    link: str
    file_attachment_type: str


class FileAttachmentDeleteBody(BasePostBody):
    name: str
