from ninja import Schema
from typing import Literal
from pydantic import validator
from sensorthings.validators import whitespace_to_none


metadataOwnerOptions = Literal[
    'currentUser', 'noUser', 'currentUserOrNoUser', 'anyUser', 'anyUserOrNoUser'
]


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