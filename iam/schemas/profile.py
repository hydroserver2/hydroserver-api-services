from ninja import Schema
from pydantic import ConfigDict, EmailStr, field_validator, StringConstraints as StrCon
from pydantic.alias_generators import to_camel
from typing import Optional, Annotated, List
from sensorthings.validators import PartialSchema
from django.conf import settings
from iam.models import Organization


class ProfileBaseSchema(Schema):
    @field_validator("*", mode="before")
    def empty_str_to_none(cls, value):
        if isinstance(value, str) and value.strip() == "":
            return None
        return value

    model_config = ConfigDict(
        populate_by_name=True, str_strip_whitespace=True, alias_generator=to_camel
    )


class OrganizationFields(ProfileBaseSchema):
    code: Annotated[str, StrCon(max_length=255)]
    name: Annotated[str, StrCon(max_length=30)]
    description: Optional[str] = None
    link: Optional[Annotated[str, StrCon(max_length=2000)]] = None
    organization_type: Annotated[str, StrCon(max_length=255)]


class OrganizationPatchFields(OrganizationFields, metaclass=PartialSchema):
    pass


class UserFields(ProfileBaseSchema):
    first_name: Annotated[str, StrCon(max_length=30)]
    middle_name: Optional[Annotated[str, StrCon(max_length=30)]] = None
    last_name: Annotated[str, StrCon(max_length=150)]
    phone: Optional[Annotated[str, StrCon(max_length=15)]] = None
    address: Optional[Annotated[str, StrCon(max_length=255)]] = None
    user_type: Optional[Annotated[str, StrCon(max_length=255)]] = None
    link: Optional[Annotated[str, StrCon(max_length=2000)]] = None
    organization: Optional[OrganizationFields] = None


class UserPatchFields(UserFields, metaclass=PartialSchema):
    organization: Optional[OrganizationPatchFields] = None


class ProfileGetResponse(UserFields):
    email: EmailStr
    is_profile_complete: bool
    is_ownership_allowed: bool
    is_active: bool


class ProfilePatchBody(UserPatchFields):
    def save(self, user: settings.AUTH_USER_MODEL):
        user_body = self.dict(include=set(self.model_fields.keys()), exclude=["organization"], exclude_unset=True)

        organization_body = self.organization.dict(
            include=set(self.organization.model_fields.keys()), exclude_unset=True
        ) if self.organization else None

        for field, value in user_body.items():
            setattr(user, field, value)

        if organization_body:
            if user.organization:
                for field, value in organization_body.items():
                    setattr(user.organization, field, value)
                user.organization.save()
            else:
                user.organization = Organization.objects.create(**organization_body)

        user.save()

        return user


class TypeGetResponse(ProfileBaseSchema):
    user_types: List[Annotated[str, StrCon(max_length=255)]]
    organization_types: List[Annotated[str, StrCon(max_length=255)]]
