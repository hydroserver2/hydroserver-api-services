from api.schemas import BaseGetResponse


class ProviderDetailResponse(BaseGetResponse):
    id: str
    name: str
    icon_link: str
    signup_enabled: bool
    connect_enabled: bool


class AuthenticationMethodsDetailResponse(BaseGetResponse):
    hydroserver_signup_enabled: bool
    providers: list[ProviderDetailResponse]
