from uuid import UUID
from ninja import Schema
from typing import Optional
from hydrothings.validators import allow_partial


class SensorFields(Schema):
    name: str
    description: Optional[str] = None
    encoding_type: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    model_url: Optional[str] = None
    method_type: Optional[str] = None
    method_link: Optional[str] = None
    method_code: Optional[str] = None


class SensorQueryParams(Schema):
    pass


class SensorGetResponse(SensorFields):
    id: UUID


class SensorPostBody(SensorFields):
    pass


@allow_partial
class SensorPatchBody(SensorFields):
    pass
