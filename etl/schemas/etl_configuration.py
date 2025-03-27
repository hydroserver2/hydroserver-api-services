import uuid
from ninja import Schema, Field
from pydantic import AliasChoices
from typing import Optional, Literal
from hydroserver.schemas import BaseGetResponse, BasePostBody, BasePatchBody


class EtlConfigurationFields(Schema):
    name: str = Field(..., max_length=255)
    etl_configuration_type: Literal["DataSource", "Datastream"] = Field(
        ..., alias="type"
    )
    etl_configuration_schema: dict = Field(..., alias="schema")


class EtlConfigurationGetResponse(BaseGetResponse, EtlConfigurationFields):
    id: uuid.UUID
    etl_system_platform_id: uuid.UUID
    workspace_id: Optional[uuid.UUID] = Field(
        None,
        validation_alias=AliasChoices(
            "workspaceId", "etl_system_platform__workspace_id"
        ),
    )


class EtlConfigurationPostBody(BasePostBody, EtlConfigurationFields):
    pass


class EtlConfigurationPatchBody(BasePatchBody, EtlConfigurationFields):
    pass
