from ninja.errors import HttpError
from django.contrib.auth import get_user_model
from iam.models import Organization, UserType, OrganizationType
from iam.schemas import AccountPostBody, AccountPatchBody

User = get_user_model()


class AccountService:
    @staticmethod
    def get(principal: User):
        return principal

    @staticmethod
    def create(data: AccountPostBody):
        try:
            user_body = data.dict(
                include=set(data.model_fields.keys()),
                exclude=["organization"],
                exclude_unset=True,
            )
            organization_body = (
                data.organization.dict(
                    include=set(data.organization.model_fields.keys()),
                    exclude_unset=True,
                )
                if data.organization
                else None
            )

            organization = (
                Organization.objects.create(**organization_body)
                if organization_body
                else None
            )
            user = User.objects.create(organization=organization, **user_body)

            return user

        except ValueError as e:
            raise HttpError(422, str(e))

    @staticmethod
    def update(principal: User, data: AccountPatchBody):
        try:
            user_body = data.dict(
                include=set(data.model_fields.keys()),
                exclude=["organization"],
                exclude_unset=True,
            )
            update_organization = "organization" in data.dict(
                include=["organization"],
                exclude_unset=True,
            )

            organization_body = (
                data.organization.dict(
                    include=set(data.organization.model_fields.keys()),
                    exclude_unset=True,
                )
                if data.organization
                else None
            )

            for field, value in user_body.items():
                setattr(principal, field, value)

            if update_organization:
                if organization_body:
                    if principal.organization:
                        for field, value in organization_body.items():
                            setattr(principal.organization, field, value)
                        principal.organization.save()
                    else:
                        principal.organization = Organization.objects.create(
                            **organization_body
                        )
                else:
                    if principal.organization:
                        principal.organization.delete()
                        principal.organization = None

        except ValueError as e:
            raise HttpError(422, str(e))

        principal.save()

        return principal

    @staticmethod
    def delete(principal: User):
        principal.delete()

        return "User account has been deleted"

    @staticmethod
    def get_types():
        return {
            "user_types": UserType.objects.filter(public=True).values_list(
                "name", flat=True
            ),
            "organization_types": OrganizationType.objects.filter(
                public=True
            ).values_list("name", flat=True),
        }
