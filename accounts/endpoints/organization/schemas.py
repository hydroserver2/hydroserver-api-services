from ninja import Schema
from sensorthings.validators import disable_required_field_validation


class OrganizationFields(Schema):
    code: str
    name: str
    description: str = None
    type: str
    link: str = None

    @classmethod
    def is_empty(cls, obj):
        return not (obj.name and obj.code and obj.type)


@disable_required_field_validation
class OrganizationPatchBody(OrganizationFields):
    pass
