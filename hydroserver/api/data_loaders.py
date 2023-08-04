from hydroserver.api.api import api
from django.db import transaction
from django.http import HttpRequest
from typing import List
from hydroserver.api.authentication import BasicAuth
from hydroserver.api.util import jwt_auth
from hydroserver.schemas import DataLoaderGetResponse, DataLoaderPatchBody, DataLoaderPostBody
from sites.models import DataLoader, DataLoaderOwner


@api.get(
    '/data-loaders',
    url_name='get_data_loaders',
    response={
        200: List[DataLoaderGetResponse]
    },
    auth=[BasicAuth(), jwt_auth]
)
def get_data_loaders(request: HttpRequest):

    data_loaders = DataLoader.objects.filter(dataloaderowner__person=request.authenticated_user)

    return [
        {
            'id': data_loader.id,
            'name': data_loader.name
        } for data_loader in data_loaders
    ]


@api.get(
    '/data-loaders/{data_loader_id}',
    url_name='get_data_loader',
    response={
        200: DataLoaderGetResponse,
        404: None
    },
    auth=[BasicAuth(), jwt_auth]
)
def get_data_loader(request: HttpRequest, data_loader_id: str):

    data_loader = DataLoader.objects.get(dataloaderowner__person=request.authenticated_user, pk=data_loader_id)

    return {
        'id': data_loader.id,
        'name': data_loader.name
    }


@api.post(
    '/data-loaders',
    url_name='create_data_loader',
    response={
        201: None
    },
    auth=[BasicAuth(), jwt_auth]
)
@transaction.atomic
def post_data_loader(request: HttpRequest, data_loader: DataLoaderPostBody):
    """"""

    new_data_loader = DataLoader.objects.create(
        name=data_loader.name,
    )

    DataLoaderOwner.objects.create(
        data_loader=new_data_loader,
        person=request.authenticated_user
    )

    return None


@api.patch(
    '/data-loaders/{data_loader_id}',
    url_name='update_data_loader',
    response={
        204: None
    },
    auth=[BasicAuth(), jwt_auth],
)
@transaction.atomic
def patch_data_loader(request: HttpRequest, data_loader_id: str, data_loader: DataLoaderPatchBody):
    """"""

    data_loader = data_loader.dict(exclude_unset=True)
    data_loader_db = DataLoader.objects.filter(
        pk=data_loader_id,
        dataloaderowner__person=request.authenticated_user,
    )[0]

    if 'name' in data_loader:
        data_loader_db.name = data_loader['name']

    data_loader_db.save()

    return None


@api.delete(
    '/data-loaders/{data_loader_id}',
    auth=[BasicAuth(), jwt_auth],
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

    if request.authenticated_user not in [
        data_loader_owner.person for data_loader_owner
        in data_loader.dataloaderowner_set.filter(is_primary_owner=True)
    ]:
        return 403, 'You do not have permission to delete this data loader.'

    data_loader.delete()

    return 200