from ninja.errors import HttpError
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from iam.models import Organization, UserType, OrganizationType
from iam.schemas import AccountPostBody, AccountPatchBody

User = get_user_model()


class AccountService:
    @staticmethod
    def get(user: User):
        return user

    @staticmethod
    def create(data: AccountPostBody):
        try:
            user_body = data.dict(include=set(data.model_fields.keys()), exclude=["organization"], exclude_unset=True)
            organization_body = data.organization.dict(
                include=set(data.organization.model_fields.keys()), exclude_unset=True
            ) if data.organization else None

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

    @staticmethod
    def update(user: User, data: AccountPatchBody):
        try:
            user_body = data.dict(include=set(data.model_fields.keys()), exclude=["organization"], exclude_unset=True)
            organization_body = data.organization.dict(
                include=set(data.organization.model_fields.keys()), exclude_unset=True
            ) if data.organization else None

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

    @staticmethod
    def delete(user: User):
        user.delete()

        return "User account has been deleted"

    @staticmethod
    def get_types():
        return {
            "user_types": UserType.objects.filter(public=True).values_list("name", flat=True),
            "organization_types": OrganizationType.objects.filter(public=True).values_list("name", flat=True),
        }
