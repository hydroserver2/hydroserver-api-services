import uuid
from ninja import Schema, Field, Query
from typing import Optional, Literal, TYPE_CHECKING
from api.schemas import (
    BaseDetailResponse,
    BasePostBody,
    BasePatchBody,
    CollectionQueryParameters,
)

if TYPE_CHECKING:
    from iam.schemas import WorkspaceDetailResponse


class OrchestrationSystemFields(Schema):
    name: str = Field(..., max_length=255)
    orchestration_system_type: str = Field(..., max_length=255, alias="type")


_order_by_fields = (
    "name",
    "type",
)

OrchestrationSystemOrderByFields = Literal[*_order_by_fields, *[f"-{f}" for f in _order_by_fields]]


class OrchestrationSystemQueryParameters(CollectionQueryParameters):
    workspace_id: list[uuid.UUID] = Query(
        [], description="Filter sensors by workspace ID."
    )
    orchestration_system_type: list[str] = Query(
        [], description="Filter orchestration systems by type.", alias="type"
    )


class OrchestrationSystemSummaryResponse(BaseDetailResponse, OrchestrationSystemFields):
    id: uuid.UUID
    workspace_id: Optional[uuid.UUID] = None


class OrchestrationSystemDetailResponse(BaseDetailResponse, OrchestrationSystemFields):
    id: uuid.UUID
    workspace: Optional["WorkspaceDetailResponse"] = None


class OrchestrationSystemPostBody(BasePostBody, OrchestrationSystemFields):
    workspace_id: Optional[uuid.UUID] = None


class OrchestrationSystemPatchBody(BasePatchBody, OrchestrationSystemFields):
    pass
