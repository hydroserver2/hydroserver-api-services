from api.schemas import BaseDetailResponse


class ProviderDetailResponse(BaseDetailResponse):
    id: str
    name: str
    icon_link: str
    signup_enabled: bool
    connect_enabled: bool


class AuthenticationMethodsDetailResponse(BaseDetailResponse):
    hydroserver_signup_enabled: bool
    providers: list[ProviderDetailResponse]
