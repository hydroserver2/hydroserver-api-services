import uuid
from typing import Optional
from ninja import Schema, Field, Query
from pydantic import field_validator, AliasChoices
from country_list import countries_for_language
from hydroserver.schemas import (
    BaseGetResponse,
    BasePostBody,
    BasePatchBody,
    CollectionQueryParameters,
)
from iam.schemas import WorkspaceGetResponse
from .tag import TagGetResponse
from .photo import PhotoGetResponse

valid_country_codes = [code for code, _ in countries_for_language("en")]


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
    state: Optional[str] = Field(
        None, max_length=200, validation_alias=AliasChoices("state", "location.state")
    )
    county: Optional[str] = Field(
        None, max_length=200, validation_alias=AliasChoices("county", "location.county")
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


class LocationGetResponse(BaseGetResponse, LocationFields):
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


class ThingQueryParameters(CollectionQueryParameters):
    workspace_id: list[uuid.UUID] = Query(
        [], description="Filter things by workspace ID."
    )
    bbox: list[str] = Query(
        [],
        description="Filter things by bounding box. Format bounding box as {min_lon},{min_lat},{max_lon},{max_lat}",
    )
    state: list[str] = Query([], description="Filter things by state.")
    county: list[str] = Query([], description="Filter things by county.")
    country: list[str] = Query([], description="Filter things by country.")
    site_type: list[str] = Query([], description="Filter things by site type.")
    sampling_feature_type: list[str] = Query(
        [], description="Filter things by sampling feature type."
    )
    sampling_feature_code: list[str] = Query(
        [], description="Filter things by sampling feature code."
    )
    tag: list[str] = Query(
        [], description="Filter things by tag. Format tag filters as {key}:{value}"
    )
    is_private: Optional[bool] = Query(
        None, description="Controls whether the things should be private or public."
    )


class ThingCollectionResponse(BaseGetResponse, ThingFields):
    id: uuid.UUID
    workspace_id: uuid.UUID
    location: LocationGetResponse
    tags: list[TagGetResponse]
    photos: list[PhotoGetResponse]


class ThingGetResponse(BaseGetResponse, ThingFields):
    id: uuid.UUID
    workspace: WorkspaceGetResponse
    location: LocationGetResponse
    tags: list[TagGetResponse]
    photos: list[PhotoGetResponse]


class ThingPostBody(BasePostBody, ThingFields):
    workspace_id: uuid.UUID
    location: LocationPostBody


class ThingPatchBody(BasePatchBody, ThingFields):
    location: LocationPatchBody
