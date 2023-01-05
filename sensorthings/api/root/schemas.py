from pydantic import Field
from ninja import Schema


class ServerSettings(Schema):
    conformance: list[str]


class ServerCapabilities(Schema):
    name: str = None
    url: str = None


class ServerRootResponse(Schema):
    server_settings: ServerSettings = Field(None, alias='serverSettings')
    server_capabilities: list[ServerCapabilities] = Field(None, alias='value')

    class Config:
        allow_population_by_field_name = True
