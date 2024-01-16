from ninja import Schema
from pydantic import validator
from sensorthings.validators import whitespace_to_none


class BasePostBody(Schema):

    _whitespace_validator = validator(
        '*',
        allow_reuse=True,
        check_fields=False,
        pre=True
    )(whitespace_to_none)


class BasePatchBody(Schema):

    _whitespace_validator = validator(
        '*',
        allow_reuse=True,
        check_fields=False,
        pre=True
    )(whitespace_to_none)