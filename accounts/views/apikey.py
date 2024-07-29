import json
from ninja import Router, Path
from typing import List
from uuid import UUID
from django.http import HttpRequest
from hydroserver.auth import JWTAuth, BasicAuth
from accounts.models import APIKey
from accounts.schemas.apikey import APIKeyGetResponse, APIKeyPostResponse, APIKeyPatchBody, APIKeyPostBody


api_key_router = Router(tags=['API Keys'])


@api_key_router.get(
    '',
    auth=[JWTAuth(), BasicAuth()],
    response={
        200: List[APIKeyGetResponse],
        401: str
    },
    by_alias=True
)
def list_api_keys(request: HttpRequest):
    """
    List API keys.

    This endpoint returns a list of all API keys owned by the authenticated user.
    """

    user = getattr(request, 'authenticated_user')
    api_keys = APIKey.objects.filter(person=user)

    return [api_key for api_key in api_keys.all()]


@api_key_router.get(
    '/{api_key_id}',
    auth=[JWTAuth(), BasicAuth()],
    response={
        200: APIKeyGetResponse,
        401: str, 403: str, 404: str
    },
    by_alias=True
)
def get_api_key(request: HttpRequest, api_key_id: UUID = Path(...)):
    """
    Get an API key.

    This endpoint returns an API key owned by the authenticated user.
    """

    user = getattr(request, 'authenticated_user')

    try:
        api_key = APIKey.objects.filter(
            id=api_key_id,
            person=user
        ).get()
    except APIKey.DoesNotExist:
        return 404, 'API key not found.'

    return api_key


@api_key_router.post(
    '',
    auth=[JWTAuth(), BasicAuth()],
    response={
        201: APIKeyPostResponse,
        401: str, 422: str
    },
    by_alias=True
)
def create_api_key(request: HttpRequest, data: APIKeyPostBody):
    """
    Create an API key.

    This endpoint allows the authenticated user to create a new API key. The user should save the token secret
    returned by the endpoint as they will not be able to get the value later.
    """

    user = getattr(request, 'authenticated_user')
    api_key = APIKey.objects.create(
        name=data.name,
        permissions=[permission.dict(exclude_unset=True) for permission in data.permissions],
        expires=data.expires,
        enabled=data.enabled,
        person=user
    )

    api_key.generate_token()

    return 201, api_key


@api_key_router.patch(
    '/{api_key_id}',
    auth=[JWTAuth(), BasicAuth()],
    response={
        203: APIKeyGetResponse,
        401: str, 403: str, 404: str, 422: str
    },
    by_alias=True
)
def update_api_key(request: HttpRequest, data: APIKeyPatchBody, api_key_id: UUID = Path(...)):
    """
    Update an API key.

    This endpoint allows the authenticated user to modify properties of an API key they own. The token secret
    cannot be modified this way.
    """

    user = getattr(request, 'authenticated_user')

    try:
        api_key = APIKey.objects.filter(
            id=api_key_id,
            person=user
        ).get()
    except APIKey.DoesNotExist:
        return 404, 'API key not found.'

    api_key_data = data.dict(exclude_unset=True)

    for field in api_key_data:
        if field == 'permissions':
            api_key.permissions = json.dumps(
                [permission.dict(exclude_unset=True) for permission in data.permissions],
                default=str
            )
        else:
            setattr(api_key, field, getattr(data, field))

    api_key.save()

    return 203, api_key


@api_key_router.delete(
    '/{api_key_id}',
    auth=[JWTAuth(), BasicAuth()],
    response={
        204: None,
        401: str, 403: str, 404: str
    },
)
def delete_api_key(request: HttpRequest, api_key_id: UUID = Path(...)):
    """
    Delete an API key.

    This endpoint allows the authenticated user to delete an API key they own.
    """

    user = getattr(request, 'authenticated_user')

    try:
        api_key = APIKey.objects.filter(
            id=api_key_id,
            person=user
        ).get()
    except APIKey.DoesNotExist:
        return 404, 'API key not found.'

    api_key.delete()
