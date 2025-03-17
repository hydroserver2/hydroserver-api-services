from ninja import Router
from iam.models import UserType, OrganizationType

iam_vocabulary_router = Router(tags=["Vocabulary"])


@iam_vocabulary_router.get(
    "/user-types",
    response={
        200: list[str]
    },
    by_alias=True
)
def get_user_types(request):
    """
    Get user types.
    """

    return 200, UserType.objects.filter(public=True).values_list("name", flat=True)


@iam_vocabulary_router.get(
    "/organization-types",
    response={
        200: list[str]
    },
    by_alias=True
)
def get_organization_types(request):
    """
    Get organization types.
    """

    return 200, OrganizationType.objects.filter(public=True).values_list("name", flat=True)
