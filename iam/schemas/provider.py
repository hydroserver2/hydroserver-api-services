from ninja import Schema
from typing import Literal


class ProviderRedirectPostForm(Schema):
    provider: str
    callback_url: str
    process: Literal["login", "connect"]
