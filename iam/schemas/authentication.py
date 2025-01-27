from ninja import Schema
from pydantic import ConfigDict
from pydantic.alias_generators import to_camel
from typing import List
from hydroserver.schemas import BaseGetResponse


class AuthenticationBaseSchema(Schema):

    model_config = ConfigDict(
        populate_by_name=True, str_strip_whitespace=True, alias_generator=to_camel
    )


class ProviderGetResponse(BaseGetResponse):
    id: str
    name: str
    icon_link: str
    signup_enabled: bool
    connect_enabled: bool


class AuthenticationMethodsGetResponse(BaseGetResponse):
    hydroserver_signup_enabled: bool
    providers: List[ProviderGetResponse]
