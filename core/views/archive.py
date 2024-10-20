import hsclient
from uuid import UUID
from ninja import Path
from ninja.errors import HttpError
from typing import Optional
from django.db import transaction, IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from core.models import Thing, Archive
from core.router import DataManagementRouter
from core.schemas.thing import ArchiveFields, ArchiveGetResponse, ArchivePostBody, ArchivePatchBody
from hydroserver import settings


router = DataManagementRouter(tags=['Archive'])


@router.dm_get('', response=Optional[ArchiveGetResponse])
def get_thing_archive(request, thing_id: UUID = Path(...)):
    """
    Get a list of Tags for a Thing

    This endpoint returns a list of tags for a thing owned by the authenticated user if there is one.
    """

    Thing.objects.get_by_id(
        thing_id=thing_id,
        user=request.authenticated_user,
        method='GET',
        raise_404=True,
        fetch=False
    )

    try:
        archive = Archive.objects.get(thing_id=thing_id)
    except ObjectDoesNotExist:
        return None

    return 200, archive


@router.dm_post('', response=ArchiveGetResponse)
@transaction.atomic
def create_archive(request, data: ArchivePostBody, thing_id: UUID = Path(...)):
    """
    Create a Thing Archive

    This endpoint creates a new archive for a thing owned by the authenticated user.
    """

    thing = Thing.objects.get_by_id(
        thing_id=thing_id,
        user=request.authenticated_user,
        method='PATCH',
        raise_404=True
    )

    if request.authenticated_user.hydroshare_token is None:
        return 403, 'You have not linked a HydroShare account to your HydroServer account.'

    try:
        if thing.archive:
            return 409, 'Thing archive already exists.'
    except Thing.archive.RelatedObjectDoesNotExist:  # noqa
        pass

    hydroshare_connection = hsclient.HydroShare(
        client_id=settings.AUTHLIB_OAUTH_CLIENTS['hydroshare']['client_id'],
        token={
            'access_token': request.authenticated_user.hydroshare_token['access_token'],
            'token_type': request.authenticated_user.hydroshare_token['token_type'],
            'scope': request.authenticated_user.hydroshare_token['scope'],
            'state': '',
            'expires_in': request.authenticated_user.hydroshare_token['expires_in'],
            'refresh_token': request.authenticated_user.hydroshare_token['refresh_token']
        }
    )

    archive = Archive.objects.create_or_link(
        hs_connection=hydroshare_connection,
        thing=thing,
        **data.dict()
    )

    archive.transfer_data(
        hs_connection=hydroshare_connection,
        make_public=data.public_resource
    )

    return 201, archive


@router.dm_post('trigger', response=ArchiveGetResponse)
@transaction.atomic
def trigger_data_archival(request, thing_id: UUID = Path(...)):
    """
    Trigger Thing Archival

    This endpoint transfers data for a thing to its HydroShare archive resource.
    """

    thing = Thing.objects.get_by_id(
        thing_id=thing_id,
        user=request.authenticated_user,
        method='PATCH',
        raise_404=True
    )

    if request.authenticated_user.hydroshare_token is None:
        return 403, 'You have not linked a HydroShare account to your HydroServer account.'

    try:
        thing.archive
    except Thing.archive.RelatedObjectDoesNotExist:  # noqa
        return 404, 'Thing archive does not exist.'

    hydroshare_connection = hsclient.HydroShare(
        client_id=settings.AUTHLIB_OAUTH_CLIENTS['hydroshare']['client_id'],
        token={
            'access_token': request.authenticated_user.hydroshare_token['access_token'],
            'token_type': request.authenticated_user.hydroshare_token['token_type'],
            'scope': request.authenticated_user.hydroshare_token['scope'],
            'state': '',
            'expires_in': request.authenticated_user.hydroshare_token['expires_in'],
            'refresh_token': request.authenticated_user.hydroshare_token['refresh_token']
        }
    )

    thing.archive.transfer_data(
        hs_connection=hydroshare_connection
    )

    return 201, thing.archive


@router.dm_patch('', response=ArchiveGetResponse)
@transaction.atomic
def update_archive(request, data: ArchivePatchBody, thing_id: UUID = Path(...)):
    """
    Update a Thing Archive

    This endpoint updates an existing archive for a thing owned by the authenticated user.
    """

    thing = Thing.objects.get_by_id(
        thing_id=thing_id,
        user=request.authenticated_user,
        method='PATCH',
        raise_404=True
    )

    if not thing.archive:
        raise HttpError(404, 'Archive for this thing not found.')

    archive_data = data.dict(include=set(ArchiveFields.model_fields.keys()), exclude_unset=True)

    hydroshare_connection = hsclient.HydroShare(
        client_id=settings.AUTHLIB_OAUTH_CLIENTS['hydroshare']['client_id'],
        token={
            'access_token': request.authenticated_user.hydroshare_token['access_token'],
            'token_type': request.authenticated_user.hydroshare_token['token_type'],
            'scope': request.authenticated_user.hydroshare_token['scope'],
            'state': '',
            'expires_in': request.authenticated_user.hydroshare_token['expires_in'],
            'refresh_token': request.authenticated_user.hydroshare_token['refresh_token']
        }
    )

    if 'link' in archive_data.keys():
        thing.archive.delete()
        thing.archive = Archive.objects.create_or_link(
            hs_connection=hydroshare_connection,
            thing=thing,
            **archive_data
        )
    else:
        for field, value in archive_data.items():
            if field == 'datastream_ids':
                for datastream in thing.datastreams.all():
                    if value and datastream.id in value:
                        datastream.archived = True
                    else:
                        datastream.archived = False
            else:
                setattr(thing.archive, field, value)

        thing.archive.save()

    thing.archive.transfer_data(
        hs_connection=hydroshare_connection,
    )

    return 203, thing.archive


@router.dm_delete('')
def delete_archive(request, thing_id: UUID = Path(...)):
    """
    Delete a Thing Archive

    This endpoint will delete an existing thing archive if the authenticated user is an owner of the
    thing. The record of the archive resource will be deleted from HydroServer, however the resource itself will
    not be deleted.
    """

    thing = Thing.objects.get_by_id(
        thing_id=thing_id,
        user=request.authenticated_user,
        method='PATCH',
        raise_404=True
    )

    if not thing.archive:
        raise HttpError(404, 'Archive for this thing not found.')

    try:
        thing.archive.delete()
    except IntegrityError as e:
        return 409, str(e)

    return 204, None
