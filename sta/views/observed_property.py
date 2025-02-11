import uuid
from ninja import Router, Path
from typing import Optional
from django.db import transaction
from hydroserver.security import bearer_auth, session_auth, anonymous_auth
from hydroserver.http import HydroServerHttpRequest
from sta.schemas import ObservedPropertyGetResponse, ObservedPropertyPostBody, ObservedPropertyPatchBody
from sta.services import ObservedPropertyService

observed_property_router = Router(tags=["Observed Properties"])
observed_property_service = ObservedPropertyService()


@observed_property_router.get(
    "",
    auth=[session_auth, bearer_auth, anonymous_auth],
    response={
        200: list[ObservedPropertyGetResponse],
        401: str,
    },
    by_alias=True
)
def get_observed_properties(request: HydroServerHttpRequest, workspace_id: Optional[uuid.UUID] = None):
    """
    Get public Observed Properties and Observed Properties associated with the authenticated user.
    """

    return 200, observed_property_service.list(
        user=request.authenticated_user,
        workspace_id=workspace_id
    )


@observed_property_router.post(
    "",
    auth=[session_auth, bearer_auth],
    response={
        201: ObservedPropertyGetResponse,
        401: str,
        422: str,
    },
    by_alias=True
)
@transaction.atomic
def create_observed_property(request: HydroServerHttpRequest, data: ObservedPropertyPostBody):
    """
    Create a new Observed Property.
    """

    return 201, observed_property_service.create(
        user=request.authenticated_user,
        data=data
    )


@observed_property_router.get(
    "/{observed_property_id}",
    auth=[session_auth, bearer_auth, anonymous_auth],
    response={
        200: ObservedPropertyGetResponse,
        401: str,
        403: str,
    },
    by_alias=True,
    exclude_unset=True
)
def get_observed_property(request: HydroServerHttpRequest, observed_property_id: Path[uuid.UUID]):
    """
    Get an Observed Property.
    """

    return 200, observed_property_service.get(
        user=request.authenticated_user,
        uid=observed_property_id
    )


@observed_property_router.patch(
    "/{observed_property_id}",
    auth=[session_auth, bearer_auth],
    response={
        200: ObservedPropertyGetResponse,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True
)
@transaction.atomic
def update_observed_property(request: HydroServerHttpRequest, observed_property_id: Path[uuid.UUID], data: ObservedPropertyPatchBody):
    """
    Update an Observed Property.
    """

    return 200, observed_property_service.update(
        user=request.authenticated_user,
        uid=observed_property_id,
        data=data
    )


@observed_property_router.delete(
    "/{observed_property_id}",
    auth=[session_auth, bearer_auth],
    response={
        204: None,
        401: str,
        403: str,
    },
    by_alias=True
)
@transaction.atomic
def delete_observed_property(request: HydroServerHttpRequest, observed_property_id: Path[uuid.UUID]):
    """
    Delete an Observed Property.
    """

    return 204, observed_property_service.delete(
        user=request.authenticated_user,
        uid=observed_property_id
    )
