from typing import List
from hydroserver.schemas import BaseGetResponse


class ProviderGetResponse(BaseGetResponse):
    id: str
    name: str
    icon_link: str
    signup_enabled: bool
    connect_enabled: bool


class AuthenticationMethodsGetResponse(BaseGetResponse):
    hydroserver_signup_enabled: bool
    providers: List[ProviderGetResponse]
