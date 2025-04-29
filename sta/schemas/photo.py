from hydroserver.schemas import BaseGetResponse, BasePostBody


class PhotoGetResponse(BaseGetResponse):
    name: str
    link: str


class PhotoPostBody(BasePostBody):
    name: str


class PhotoDeleteBody(BasePostBody):
    name: str
