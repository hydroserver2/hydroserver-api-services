from ninja import Schema, Query
from typing import Optional
from pydantic import AliasGenerator, AliasChoices, ConfigDict, field_validator
from pydantic.alias_generators import to_camel
from sensorthings.validators import PartialSchema


base_alias_generator = AliasGenerator(
    serialization_alias=lambda field_name: to_camel(field_name),
    validation_alias=lambda field_name: AliasChoices(to_camel(field_name), field_name),
)


class BaseQueryParameters(Schema):
    model_config = ConfigDict(
        populate_by_name=True, str_strip_whitespace=True, alias_generator=to_camel
    )


class CollectionQueryParameters(BaseQueryParameters):
    page: int = Query(1, ge=1, description="Page number (1-based).")
    page_size: int = Query(100, ge=1, description="The number of items per page.")
    ordering: Optional[str] = Query(
        None,
        description="Comma-separated list of fields to order by. Use '-' prefix for descending.",
    )


class BaseGetResponse(Schema):
    model_config = ConfigDict(
        populate_by_name=True, str_strip_whitespace=True, alias_generator=to_camel
    )


class BasePostBody(Schema):
    @field_validator("*", mode="before")
    def empty_str_to_none(cls, value):
        if isinstance(value, str) and value.strip() == "":
            return None
        return value

    model_config = ConfigDict(
        populate_by_name=True, str_strip_whitespace=True, alias_generator=to_camel
    )


class BasePatchBody(Schema, metaclass=PartialSchema):
    @field_validator("*", mode="before")
    def empty_str_to_none(cls, value):
        if isinstance(value, str) and value.strip() == "":
            return None
        return value

    model_config = ConfigDict(
        populate_by_name=True, str_strip_whitespace=True, alias_generator=to_camel
    )
