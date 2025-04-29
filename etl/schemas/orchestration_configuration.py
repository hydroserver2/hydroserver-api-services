from typing import Optional, Literal
from datetime import datetime
from ninja import Schema, Field
from hydroserver.schemas import BaseGetResponse, BasePostBody, BasePatchBody


class OrchestrationConfigurationScheduleFields(Schema):
    interval: Optional[int] = Field(None, gt=0)
    interval_units: Optional[Literal["minutes", "hours", "days"]] = None
    crontab: Optional[str] = Field(None, max_length=255)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class OrchestrationConfigurationScheduleGetResponse(
    BaseGetResponse, OrchestrationConfigurationScheduleFields
):
    pass


class OrchestrationConfigurationSchedulePostBody(
    BasePostBody, OrchestrationConfigurationScheduleFields
):
    pass


class OrchestrationConfigurationSchedulePatchBody(
    BasePatchBody, OrchestrationConfigurationScheduleFields
):
    pass


class OrchestrationConfigurationStatusFields(Schema):
    last_run_successful: Optional[bool] = None
    last_run_message: Optional[str] = Field(None, max_length=255)
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    paused: bool = False


class OrchestrationConfigurationStatusGetResponse(
    BaseGetResponse, OrchestrationConfigurationStatusFields
):
    pass


class OrchestrationConfigurationStatusPostBody(
    BasePostBody, OrchestrationConfigurationStatusFields
):
    pass


class OrchestrationConfigurationStatusPatchBody(
    BasePatchBody, OrchestrationConfigurationStatusFields
):
    pass
