import uuid
from typing import Optional, Literal, TYPE_CHECKING
from ninja import Schema, Field, Query
from pydantic import field_validator, AliasChoices
from country_list import countries_for_language
from api.schemas import (
    BaseGetResponse,
    BasePostBody,
    BasePatchBody,
    CollectionQueryParameters,
)

if TYPE_CHECKING:
    from iam.schemas import WorkspaceSummaryResponse

valid_country_codes = [code for code, _ in countries_for_language("en")]


class TagGetResponse(BaseGetResponse):
    key: str
    value: str


class TagPostBody(BasePostBody):
    key: str
    value: str


class TagDeleteBody(BasePostBody):
    key: str
    value: Optional[str] = None


class PhotoGetResponse(BaseGetResponse):
    name: str
    link: str


class PhotoPostBody(BasePostBody):
    name: str


class PhotoDeleteBody(BasePostBody):
    name: str


class LocationFields(Schema):
    latitude: float = Field(
        ...,
        ge=-90,
        le=90,
        validation_alias=AliasChoices("latitude", "location.latitude"),
    )
    longitude: float = Field(
        ...,
        ge=-180,
        le=180,
        validation_alias=AliasChoices("longitude", "location.longitude"),
    )
    elevation_m: Optional[float] = Field(
        None,
        ge=-99999,
        le=99999,
        alias="elevation_m",
        validation_alias=AliasChoices("elevation_m", "location.elevation_m"),
    )
    elevation_datum: Optional[str] = Field(
        None,
        max_length=255,
        validation_alias=AliasChoices("elevationDatum", "location.elevation_datum"),
    )
    admin_area_1: Optional[str] = Field(
        None, max_length=200, validation_alias=AliasChoices("admin_area_1", "location.admin_area_1")
    )
    admin_area_2: Optional[str] = Field(
        None, max_length=200, validation_alias=AliasChoices("admin_area_2", "location.admin_area_2")
    )
    country: Optional[str] = Field(
        None, max_length=2, validation_alias=AliasChoices("country", "location.country")
    )

    @field_validator("country", mode="after")
    def check_country_code(cls, value):
        if value and value.upper() not in valid_country_codes:
            raise ValueError(
                f"Invalid country code: {value}. Must be an ISO 3166-1 alpha-2 country code."
            )
        return value


class LocationDetailResponse(BaseGetResponse, LocationFields):
    pass


class LocationPostBody(BasePostBody, LocationFields):
    pass


class LocationPatchBody(BasePatchBody, LocationFields):
    pass


class ThingFields(Schema):
    name: str = Field(..., max_length=200)
    description: str
    sampling_feature_type: str = Field(..., max_length=200)
    sampling_feature_code: str = Field(..., max_length=200)
    site_type: str = Field(..., max_length=200)
    data_disclaimer: Optional[str] = None
    is_private: bool


_order_by_fields = (
    "name",
    "samplingFeatureType",
    "samplingFeatureCode",
    "siteType",
    "isPrivate",
    "latitude",
    "longitude",
    "elevation_m",
    "elevationDatum",
    "admin_area_1",
    "admin_area_2",
    "country",
)

ThingOrderByFields = Literal[*_order_by_fields, *[f"-{f}" for f in _order_by_fields]]


class ThingQueryParameters(CollectionQueryParameters):
    expand_related: Optional[bool] = None
    order_by: Optional[list[ThingOrderByFields]] = Query(
        [], description="Select one or more fields to order the response by."
    )
    workspace_id: list[uuid.UUID] = Query(
        [], description="Filter things by workspace ID."
    )
    bbox: list[str] = Query(
        [],
        description="Filter things by bounding box. Format bounding box as {min_lon},{min_lat},{max_lon},{max_lat}",
    )
    locations__admin_area_1: list[str] = Query(
        [], description="Filter things by admin area 1.", alias="admin_area_1"
    )
    locations__admin_area_2: list[str] = Query(
        [], description="Filter things by admin area 2.", alias="admin_area_2"
    )
    locations__country: list[str] = Query(
        [], description="Filter things by country.", alias="country"
    )
    site_type: list[str] = Query([], description="Filter things by site type.")
    sampling_feature_type: list[str] = Query(
        [], description="Filter things by sampling feature type."
    )
    tag: list[str] = Query(
        [], description="Filter things by tag. Format tag filters as {key}:{value}"
    )
    is_private: Optional[bool] = Query(
        None,
        description="Controls whether the returned things should be private or public.",
    )


class ThingSummaryResponse(BaseGetResponse, ThingFields):
    id: uuid.UUID
    workspace_id: uuid.UUID
    location: LocationDetailResponse
    tags: list[TagGetResponse]
    photos: list[PhotoGetResponse]


class ThingDetailResponse(BaseGetResponse, ThingFields):
    id: uuid.UUID
    workspace: "WorkspaceSummaryResponse"
    location: LocationDetailResponse
    tags: list[TagGetResponse]
    photos: list[PhotoGetResponse]


class ThingPostBody(BasePostBody, ThingFields):
    workspace_id: uuid.UUID
    location: LocationPostBody


class ThingPatchBody(BasePatchBody, ThingFields):
    location: Optional[LocationPatchBody] = None
