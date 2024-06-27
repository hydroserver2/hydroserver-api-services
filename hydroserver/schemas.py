from ninja import Schema
from pydantic import field_validator, AliasGenerator, AliasChoices
from pydantic.alias_generators import to_camel
from sensorthings.validators import remove_whitespace, PartialSchema


base_alias_generator = AliasGenerator(
    serialization_alias=lambda field_name: to_camel(field_name),
    validation_alias=lambda field_name: AliasChoices(to_camel(field_name), field_name),
)


class BaseGetResponse(Schema):
    class Config:
        alias_generator = base_alias_generator


class BasePostBody(Schema):

    _whitespace_validator = field_validator(
        '*',
        check_fields=False
    )(remove_whitespace)

    class Config:
        alias_generator = base_alias_generator


class BasePatchBody(Schema, metaclass=PartialSchema):

    _whitespace_validator = field_validator(
        '*',
        check_fields=False
    )(remove_whitespace)

    class Config:
        alias_generator = base_alias_generator
