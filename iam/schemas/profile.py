from ninja import Schema, Field
from ninja.errors import ValidationError
from pydantic import ConfigDict, EmailStr, field_validator
from pydantic.alias_generators import to_camel
from typing import Optional, List, Literal
from sensorthings.validators import PartialSchema
from django.db import IntegrityError
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
    code: str = Field(..., max_length=255)
    name: str = Field(..., max_length=30)
    description: Optional[str] = None
    link: Optional[str] = Field(None, max_length=2000)
    organization_type: str = Field(..., max_length=255, alias='type')


class OrganizationPatchFields(OrganizationFields, metaclass=PartialSchema):
    pass


class UserFields(ProfileBaseSchema):
    first_name: str = Field(..., max_length=30)
    middle_name: Optional[str] = Field(None, max_length=30)
    last_name: str = Field(..., max_length=150)
    phone: Optional[str] = Field(None, max_length=15)
    address: Optional[str] = Field(None, max_length=255)
    user_type: str = Field(..., max_length=255, alias='type')
    link: Optional[str] = Field(None, max_length=2000)
    organization: Optional[OrganizationFields] = None


class UserPatchFields(UserFields, metaclass=PartialSchema):
    organization: Optional[OrganizationPatchFields] = None


class ProfileGetResponse(UserFields):
    email: EmailStr
    account_type: Literal["Admin", "Standard", "Limited"]
    account_status: Literal["Active", "Disabled", "Incomplete", "Unverified"]


class ProfilePatchBody(UserPatchFields):
    def save(self, user: settings.AUTH_USER_MODEL):
        try:
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
        except IntegrityError as e:
            error_message = str(e)
            if "user_type" in error_message:
                raise ValidationError([{"detail": "Invalid userType value provided."}])
            if "organization_type" in error_message:
                raise ValidationError([{"detail": "Invalid organizationType value provided."}])

        user.save()

        return user


class TypeGetResponse(ProfileBaseSchema):
    user_types: List[str]
    organization_types: List[str]
