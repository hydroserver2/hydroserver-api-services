from ninja import Schema, Field
from ninja.errors import HttpError
from pydantic import EmailStr
from typing import List, Optional, Literal
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from hydroserver.schemas import BaseGetResponse, BasePostBody, BasePatchBody
from iam.models import Organization


User = get_user_model()


class OrganizationFields(Schema):
    code: str = Field(..., max_length=255)
    name: str = Field(..., max_length=30)
    description: Optional[str] = None
    link: Optional[str] = Field(None, max_length=2000)
    organization_type: str = Field(..., max_length=255, alias='type')


class OrganizationPostBody(BasePostBody, OrganizationFields):
    pass


class OrganizationPatchBody(BasePatchBody, OrganizationFields):
    pass


class UserFields(Schema):
    first_name: str = Field(..., max_length=30)
    middle_name: Optional[str] = Field(None, max_length=30)
    last_name: str = Field(..., max_length=150)
    phone: Optional[str] = Field(None, max_length=15)
    address: Optional[str] = Field(None, max_length=255)
    user_type: str = Field(..., max_length=255, alias='type')
    link: Optional[str] = Field(None, max_length=2000)
    organization: Optional[OrganizationFields] = None


class AccountGetResponse(BaseGetResponse, UserFields):
    email: EmailStr
    account_type: Literal["admin", "standard", "limited"]


class AccountPostBody(BasePostBody, UserFields):
    email: EmailStr
    password: str
    organization: Optional[OrganizationPostBody] = None

    def save(self):
        try:
            user_body = self.dict(include=set(self.model_fields.keys()), exclude=["organization"], exclude_unset=True)
            organization_body = self.organization.dict(
                include=set(self.organization.model_fields.keys()), exclude_unset=True
            ) if self.organization else None

            organization = Organization.objects.create(**organization_body) if organization_body else None
            user = User.objects.create(organization=organization, **user_body)

            return user

        except ValueError as e:
            raise HttpError(422, str(e))

        except IntegrityError as e:
            error_message = str(e)
            if "user_type" in error_message:
                raise HttpError(422, str("Invalid userType value provided."))
            if "organization_type" in error_message:
                raise HttpError(422, str("Invalid organizationType value provided."))


class AccountPatchBody(BasePatchBody, UserFields):
    organization: Optional[OrganizationPatchBody] = None

    def save(self, user: User):
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

        except ValueError as e:
            raise HttpError(422, str(e))

        except IntegrityError as e:
            error_message = str(e)
            if "user_type" in error_message:
                raise HttpError(422, str("Invalid userType value provided."))
            if "organization_type" in error_message:
                raise HttpError(422, str("Invalid organizationType value provided."))

        user.save()

        return user


class TypeGetResponse(BaseGetResponse):
    user_types: List[str]
    organization_types: List[str]
