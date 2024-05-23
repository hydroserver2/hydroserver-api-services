from ninja import Schema
from typing import Literal
from pydantic import field_validator
from sensorthings.validators import remove_whitespace


metadataOwnerOptions = Literal[
    'currentUser', 'noUser', 'currentUserOrNoUser', 'anyUser', 'anyUserOrNoUser'
]


class BasePostBody(Schema):

    _whitespace_validator = field_validator(
        '*',
        check_fields=False
    )(remove_whitespace)


class BasePatchBody(Schema):

    _whitespace_validator = field_validator(
        '*',
        check_fields=False
    )(remove_whitespace)
