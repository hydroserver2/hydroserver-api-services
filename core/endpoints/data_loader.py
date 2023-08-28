from django.http import HttpRequest
from django.db import transaction

from ninja import Schema, Router
from typing import List
from uuid import UUID
from sensorthings.validators import allow_partial

from core.models import DataLoader
from accounts.auth import BasicAuth, JWTAuth

router = Router(tags=['Data Loaders'])


class DataLoaderGetResponse(Schema):
    id: UUID
    name: str


class DataLoaderPostBody(Schema):
    name: str


@allow_partial
class DataLoaderPatchBody(Schema):
    name: str


@router.get(
    '',
    url_name='get_data_loaders',
    response={
        200: List[DataLoaderGetResponse]
    },
    auth=[BasicAuth(), JWTAuth()]
)
def get_data_loaders(request: HttpRequest):

    data_loaders = DataLoader.objects.filter(person=getattr(request, 'authenticated_user'))

    return [
        {
            'id': data_loader.id,
            'name': data_loader.name
        } for data_loader in data_loaders
    ]


@router.get(
    '/{data_loader_id}',
    url_name='get_data_loader',
    response={
        200: DataLoaderGetResponse,
        404: None
    },
    auth=[BasicAuth(), JWTAuth()]
)
def get_data_loader(request: HttpRequest, data_loader_id: str):

    data_loader = DataLoader.objects.get(
        person=getattr(request, 'authenticated_user'), pk=data_loader_id
    )

    return {
        'id': data_loader.id,
        'name': data_loader.name
    }


@router.post(
    '',
    url_name='create_data_loader',
    response={
        201: None
    },
    auth=[BasicAuth(), JWTAuth()]
)
@transaction.atomic
def post_data_loader(request: HttpRequest, data_loader: DataLoaderPostBody):
    """"""

    DataLoader.objects.create(
        person=getattr(request, 'authenticated_user'),
        name=data_loader.name,
    )

    return None


@router.patch(
    '/{data_loader_id}',
    url_name='update_data_loader',
    response={
        204: None
    },
    auth=[BasicAuth(), JWTAuth()],
)
@transaction.atomic
def patch_data_loader(request: HttpRequest, data_loader_id: str, data_loader: DataLoaderPatchBody):
    """"""

    data_loader = data_loader.dict(exclude_unset=True)
    data_loader_db = DataLoader.objects.filter(
        pk=data_loader_id,
        person=getattr(request, 'authenticated_user'),
    )[0]

    if 'name' in data_loader:
        data_loader_db.name = data_loader['name']

    data_loader_db.save()

    return None


@router.delete(
    '/{data_loader_id}',
    auth=[BasicAuth(), JWTAuth()],
    response={
        200: None,
        403: None,
        404: None
    },
)
def delete_data_loader(request: HttpRequest, data_loader_id: str):
    try:
        data_loader = DataLoader.objects.get(id=data_loader_id)
    except DataLoader.DoesNotExist:
        return 404, f'Data Loader with ID: {data_loader_id} does not exist.'

    if data_loader.person != getattr(request, 'authenticated_user'):
        return 403, 'You do not have permission to delete this data loader.'

    data_loader.delete()

    return 200
