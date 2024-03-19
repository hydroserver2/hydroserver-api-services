from ninja import Schema
from sensorthings.validators import allow_partial


class OrganizationFields(Schema):
    code: str
    name: str
    description: str = None
    type: str
    link: str = None

    @classmethod
    def is_empty(cls, obj):
        return not (obj.name and obj.code and obj.type)


@allow_partial
class OrganizationPatchBody(OrganizationFields):
    pass
