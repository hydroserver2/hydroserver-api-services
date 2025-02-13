from hydroserver.schemas import BaseGetResponse, BasePostBody


class TagGetResponse(BaseGetResponse):
    key: str
    value: str


class TagPostBody(BasePostBody):
    key: str
    value: str


class TagDeleteBody(BasePostBody):
    key: str
