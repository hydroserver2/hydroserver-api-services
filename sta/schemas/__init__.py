from .thing import (
    ThingSummaryResponse,
    ThingDetailResponse,
    ThingPostBody,
    ThingPatchBody,
    ThingQueryParameters,
    LocationPostBody,
    LocationPatchBody,
    TagGetResponse,
    FileAttachmentGetResponse,
)
from .observed_property import (
    ObservedPropertySummaryResponse,
    ObservedPropertyDetailResponse,
    ObservedPropertyQueryParameters,
    ObservedPropertyPostBody,
    ObservedPropertyPatchBody,
)
from .processing_level import (
    ProcessingLevelSummaryResponse,
    ProcessingLevelDetailResponse,
    ProcessingLevelQueryParameters,
    ProcessingLevelPostBody,
    ProcessingLevelPatchBody,
)
from .result_qualifier import (
    ResultQualifierSummaryResponse,
    ResultQualifierDetailResponse,
    ResultQualifierQueryParameters,
    ResultQualifierPostBody,
    ResultQualifierPatchBody,
)
from .sensor import (
    SensorSummaryResponse,
    SensorDetailResponse,
    SensorQueryParameters,
    SensorPostBody,
    SensorPatchBody,
)
from .unit import (
    UnitSummaryResponse,
    UnitDetailResponse,
    UnitQueryParameters,
    UnitPostBody,
    UnitPatchBody,
)
from .datastream import (
    DatastreamSummaryResponse,
    DatastreamDetailResponse,
    DatastreamQueryParameters,
    DatastreamPostBody,
    DatastreamPatchBody,
)
from .observation import (
    ObservationSummaryResponse,
    ObservationDetailResponse,
    ObservationQueryParameters,
    ObservationRowResponse,
    ObservationColumnarResponse,
    ObservationPostBody,
    ObservationBulkPostQueryParameters,
    ObservationBulkPostBody,
    ObservationBulkDeleteBody,
)
from .attachment import (TagGetResponse, TagPostBody, TagDeleteBody, FileAttachmentPostBody, FileAttachmentDeleteBody,
                         FileAttachmentGetResponse)


from iam.schemas import WorkspaceSummaryResponse
from etl.schemas import DataSourceSummaryResponse


ThingDetailResponse.model_rebuild()
ObservedPropertyDetailResponse.model_rebuild()
ProcessingLevelDetailResponse.model_rebuild()
ResultQualifierDetailResponse.model_rebuild()
SensorDetailResponse.model_rebuild()
UnitDetailResponse.model_rebuild()
DatastreamDetailResponse.model_rebuild()
ObservationDetailResponse.model_rebuild()
