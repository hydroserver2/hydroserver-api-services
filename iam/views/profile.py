from ninja import Router
from django.conf import settings
from hydroserver.http import HydroServerHttpRequest
from hydroserver.security import session_auth, basic_auth, anonymous_auth
from ..models import UserType, OrganizationType
from ..schemas.profile import ProfileGetResponse, TypeGetResponse, ProfilePatchBody


profile_router = Router(tags=["Profiles"])
type_router = Router(tags=["Types"])


@profile_router.get(
    "",
    auth=[session_auth, basic_auth],
    response={
        200: ProfileGetResponse,
        401: str
    },
    by_alias=True
)
def get_profile(request: HydroServerHttpRequest):
    """
    Get user profile details.
    """

    if not request.authenticated_user:
        user = dict(request.session).get("socialaccount_sociallogin", {}).get("user")
        user["account_type"] = "Standard" if settings.ACCOUNT_OWNERSHIP_ENABLED is True else "Limited"
        user["account_status"] = "Incomplete"

        return user

    return request.authenticated_user


@profile_router.patch(
    "",
    auth=[session_auth, basic_auth],
    response={
        203: ProfileGetResponse,
        401: str
    },
    by_alias=True
)
def update_profile(request: HydroServerHttpRequest, data: ProfilePatchBody):
    """
    Update user profile details.
    """

    data.save(user=request.authenticated_user)

    return 203, request.authenticated_user


@profile_router.delete(
    "",
    auth=[session_auth, basic_auth],
    response={
        204: None,
        401: str
    }
)
def delete_profile(request: HydroServerHttpRequest):
    """
    Delete a user profile.
    """

    request.authenticated_user.delete()


@type_router.get(
    "",
    auth=[anonymous_auth],
    response={
        200: TypeGetResponse
    },
    by_alias=True
)
def get_types(request: HydroServerHttpRequest):
    """
    Get allowed user and organization types.
    """

    return {
        "user_types": UserType.objects.filter(public=True).values_list("name", flat=True),
        "organization_types": OrganizationType.objects.filter(public=True).values_list("name", flat=True),
    }
