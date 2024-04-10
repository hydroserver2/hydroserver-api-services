import os
import hsclient
import tempfile
from ninja import Path
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from django.db import transaction, IntegrityError
from django.db.models import Q
from hydroserver.auth import JWTAuth, BasicAuth, anonymous_auth
from accounts.models import Person
from core.models import Thing, Location, ThingAssociation
from core.router import DataManagementRouter
from core.schemas.thing import ThingGetResponse, ThingPostBody, ThingPatchBody, ThingOwnershipPatchBody, \
    ThingPrivacyPatchBody, ThingFields, LocationFields

# from core.endpoints.unit.utils import query_units, build_unit_response, transfer_unit_ownership
# from core.endpoints.observedproperty.utils import query_observed_properties, build_observed_property_response, \
#     transfer_observed_property_ownership
# from core.endpoints.processinglevel.utils import query_processing_levels, build_processing_level_response, \
#     transfer_processing_level_ownership
# from core.endpoints.datastream.utils import query_datastreams, build_datastream_response, generate_csv
# from core.endpoints.datastream.schemas import DatastreamGetResponse
# from core.endpoints.sensor.utils import query_sensors, build_sensor_response, transfer_sensor_ownership
# from .schemas import ThingGetResponse, ThingPostBody, ThingPatchBody, ThingOwnershipPatchBody, ThingPrivacyPatchBody, \
#     ThingMetadataGetResponse, LocationFields, ThingFields, ThingArchiveBody
# from .utils import query_things, get_thing_by_id, build_thing_response, check_thing_by_id, \
#     create_hydroshare_archive_resource
from hydroserver import settings


router = DataManagementRouter(tags=['Things'])


@router.dm_list('', response=ThingGetResponse)
def get_things(
        request,
        modified_since: Optional[datetime] = None,
        owned_only: Optional[bool] = False,
        primary_owned_only: Optional[bool] = False
):
    """
    Get a list of Things

    This endpoint returns a list of public things and things owned by the authenticated user if there is one.
    """

    thing_query = Thing.objects.select_related('location').prefetch_associates().prefetch_related('tags')
    thing_query = thing_query.modified_since(modified_since)
    thing_query = thing_query.owner_is_active()

    if primary_owned_only is True:
        thing_query = thing_query.primary_owner(user=request.authenticated_user)
    elif owned_only is True:
        thing_query = thing_query.owner(user=request.authenticated_user)
    else:
        thing_query = thing_query.owner(user=request.authenticated_user, include_public=True)

    if request.authenticated_user and request.authenticated_user.permissions.enabled():
        thing_query = thing_query.apply_permissions(user=request.authenticated_user, method='GET')

    thing_query = thing_query.distinct()

    response = [
        thing.serialize(request.authenticated_user) for thing in thing_query.all()
    ]

    return 200, response


@router.dm_get('{thing_id}', response=ThingGetResponse)
def get_thing(request, thing_id: UUID = Path(...)):
    """
    Get details for a Thing

    This endpoint returns details for a thing given a thing ID.
    """

    thing = Thing.objects.get_by_id(
        thing_id=thing_id,
        user=request.authenticated_user,
        method='GET',
        raise_404=True
    )

    return 200, thing.serialize(request.authenticated_user)


@router.dm_post('', response=ThingGetResponse)
@transaction.atomic
def create_thing(request, data: ThingPostBody):
    """
    Create a Thing

    This endpoint will create a new thing owned by the authenticated user and returns the created thing.
    """

    location = Location.objects.create(
        name=f'Location for {data.name}',
        description='location',
        encoding_type="application/geo+json",
        **data.dict(include=set(LocationFields.__fields__.keys()))
    )

    thing = Thing.objects.create(
        location=location,
        **data.dict(include=set(ThingFields.__fields__.keys()))
    )

    ThingAssociation.objects.create(
        thing=thing,
        person=request.authenticated_user,
        owns_thing=True,
        is_primary_owner=True
    )

    return 201, thing.serialize(request.authenticated_user)


@router.dm_patch('{thing_id}', response=ThingGetResponse)
@transaction.atomic
def update_thing(request, data: ThingPatchBody, thing_id: UUID = Path(...)):
    """
    Update a Thing

    This endpoint will update an existing thing owned by the authenticated user and return the updated thing.
    """

    thing = Thing.objects.get_by_id(
        thing_id=thing_id,
        user=request.authenticated_user,
        method='PATCH',
        raise_404=True
    )
    location = thing.location

    thing_data = data.dict(include=set(ThingFields.__fields__.keys()), exclude_unset=True)
    location_data = data.dict(include=set(LocationFields.__fields__.keys()), exclude_unset=True)

    if not request.authenticated_user.permissions.check_allowed_fields(
            'Thing', fields=[*thing_data.keys(), *location_data.keys()]
    ):
        return 403, 'You do not have permission to modify all the given fields of this thing.'

    if thing_data.get('name'):
        location_data['name'] = f'Location for {thing_data["name"]}'

    for field, value in thing_data.items():
        setattr(thing, field, value)

    thing.save()

    for field, value in location_data.items():
        setattr(location, field, value)

    location.save()

    return 203, thing.serialize(request.authenticated_user)


@router.dm_delete('{thing_id}')
def delete_thing(request, thing_id: UUID = Path(...)):
    """
    Delete a Thing

    This endpoint will delete an existing thing if the authenticated user is the primary owner of the thing.
    """

    thing = Thing.objects.get_by_id(
        thing_id=thing_id,
        user=request.authenticated_user,
        method='DELETE',
        raise_404=True
    )

    try:
        thing.location.delete()
    except IntegrityError as e:
        return 409, str(e)

    return 204, None


@router.patch(
    '{thing_id}/ownership',
    auth=[JWTAuth(), BasicAuth()],
    response={
        203: ThingGetResponse,
        401: str,
        403: str,
        404: str,
        422: str,
        500: str
    },
    by_alias=True
)
@transaction.atomic
def update_thing_ownership(request, data: ThingOwnershipPatchBody, thing_id: UUID = Path(...)):
    """
    Update a Thing's Ownership

    This endpoint allows a thing owner to modify the ownership of the thing for other users. Only one type of
    modification can happen per request. Possible options are "make_owner", "remove_owner", and "transfer_primary".
    """

    thing = Thing.objects.get_by_id(thing_id, request.authenticated_user, method='PATCH', raise_404=True)

    authenticated_user_association = next(iter([
        associate for associate in thing.associates.all()
        if associate.person == request.authenticated_user
    ]), None)

    try:
        user = Person.objects.get(email=data.email)
    except Person.DoesNotExist:
        return 404, 'User with the given email not found.'

    if request.authenticated_user == user and authenticated_user_association.is_primary_owner:
        return 403, 'Primary owner cannot edit their own ownership.'

    if request.authenticated_user != user and not authenticated_user_association.is_primary_owner:
        return 403, 'You do not have permission to modify this Thing\'s ownership.'

    thing_association, created = ThingAssociation.objects.get_or_create(
        thing=thing, person=user
    )

    if data.transfer_primary:
        if not authenticated_user_association.is_primary_owner:
            return 403, 'Only primary owner can transfer primary ownership.'
        datastreams = thing.datastreams.all()
        for datastream in datastreams:
            transfer_observed_property_ownership(datastream, user, request.authenticated_user)
            transfer_processing_level_ownership(datastream, user, request.authenticated_user)
            transfer_unit_ownership(datastream, user, request.authenticated_user)
            transfer_sensor_ownership(datastream, user, request.authenticated_user)
        authenticated_user_association.is_primary_owner = False
        authenticated_user_association.save()
        thing_association.is_primary_owner = True
        thing_association.owns_thing = True
        thing_association.follows_thing = False
        thing_association.save()

    elif data.remove_owner:
        if thing_association.is_primary_owner:
            return 400, 'Cannot remove primary owner.'
        thing_association.delete()

    elif data.make_owner:
        if not created:
            return 422, 'Specified user is already an owner of this site.'
        thing_association.owns_thing = True
        thing_association.follows_thing = False
        thing_association.save()

    return 203, thing.serialize(user=request.authenticated_user)


@router.patch(
    '{thing_id}/privacy',
    auth=[JWTAuth(), BasicAuth()],
    response={
        203: ThingGetResponse,
        401: str,
        403: str,
        404: str,
        500: str
    },
    by_alias=True
)
@transaction.atomic
def update_thing_privacy(request, data: ThingPrivacyPatchBody, thing_id: UUID = Path(...)):
    """
    Update a Thing's Privacy

    This endpoint allows the owner of a Thing to toggle it between a private and public resource.
    """

    thing = Thing.objects.get_by_id(thing_id, request.authenticated_user, method='PATCH', raise_404=True)

    thing.is_private = data.is_private

    if data.is_private:
        for thing_association in thing.associates.all():
            if thing_association.follows_thing:
                thing_association.delete()

    thing.save()

    return 203, thing.serialize(user=request.authenticated_user)


# # @router.patch(
# #     '{thing_id}/followership',
# #     auth=[JWTAuth(), BasicAuth()],
# #     response={
# #         203: ThingGetResponse,
# #         401: str,
# #         403: str,
# #         404: str,
# #         500: str
# #     },
# #     by_alias=True
# # )
# # @transaction.atomic
# # def update_thing_followership(request, thing_id: UUID = Path(...)):
# #     """
# #     Update a Thing's Follower Status
#
# #     This endpoint allows a user to follow or unfollow a public Thing. Users cannot follow Things they own.
# #     """
#
# #     thing = get_thing_by_id(
# #         user=request.authenticated_user,
# #         thing_id=thing_id,
# #         require_unaffiliated=True,
# #         raise_http_errors=True
# #     )
#
# #     user_association = next(iter([
# #         associate for associate in thing.associates.all()
# #         if associate.follows_thing is True and associate.person == request.authenticated_user
# #     ]), None)
#
# #     if user_association:
# #         user_association.delete()
# #     else:
# #         ThingAssociation.objects.create(
# #             thing_id=thing_id,
# #             person=request.authenticated_user,
# #             follows_thing=True
# #         )
#
# #     thing = get_thing_by_id(
# #         user=request.authenticated_user,
# #         thing_id=thing_id
# #     )
#
# #     return 203, build_thing_response(request.authenticated_user, thing)
#
#
# @router.get(
#     '{thing_id}/metadata',
#     auth=[JWTAuth(), BasicAuth(), anonymous_auth],
#     response={
#         200: ThingMetadataGetResponse,
#         401: str,
#         403: str,
#         404: str
#     },
#     by_alias=True
# )
# def get_thing_metadata(request, thing_id: UUID = Path(...)):
#     """
#     Get metadata for a Thing
#
#     This endpoint returns all metadata objects used for a given Thing. The metadata properties returned include
#     units, observed properties, sensors, and processing levels.
#     """
#
#     thing = get_thing_by_id(
#         user=request.authenticated_user,
#         thing_id=thing_id,
#         raise_http_errors=True
#     )
#
#     primary_owner = next(iter([
#         associate.person for associate in thing.associates.all()
#         if associate.is_primary_owner is True
#     ]), None)
#
#     units, _ = query_units(user=primary_owner, require_ownership_or_unowned=True)
#     sensors, _ = query_sensors(user=primary_owner, require_ownership_or_unowned=True)
#     processing_levels, _ = query_processing_levels(user=primary_owner, require_ownership_or_unowned=True)
#     observed_properties, _ = query_observed_properties(user=primary_owner, require_ownership_or_unowned=True)
#
#     units = units.filter(
#         ~Q(person=None) |
#         Q(datastreams__thing__id__in=[thing_id]) |
#         Q(time_aggregation_interval_units__thing__id__in=[thing_id])
#     ).distinct()
#     sensors = sensors.filter(~Q(person=None) | Q(datastreams__thing__id__in=[thing_id])).distinct()
#     processing_levels = processing_levels.filter(~Q(person=None) | Q(datastreams__thing__id__in=[thing_id])).distinct()
#     observed_properties = observed_properties.filter(
#         ~Q(person=None) | Q(datastreams__thing__id__in=[thing_id])
#     ).distinct()
#
#     unit_data = [build_unit_response(unit) for unit in units.all()]
#     sensor_data = [build_sensor_response(sensor) for sensor in sensors.all()]
#     processing_level_data = [build_processing_level_response(pl) for pl in processing_levels.all()]
#     observed_property_data = [build_observed_property_response(op) for op in observed_properties.all()]
#
#     return 200, {
#         'units': unit_data,
#         'sensors': sensor_data,
#         'processing_levels': processing_level_data,
#         'observed_properties': observed_property_data
#     }
#
#
# @router.get(
#     '{thing_id}/datastreams',
#     auth=[JWTAuth(), BasicAuth(), anonymous_auth],
#     response={
#         200: List[DatastreamGetResponse]
#     },
#     by_alias=True
# )
# def get_datastreams(request, thing_id: UUID = Path(...)):
#     """
#     Get a list of Datastreams for a Thing
#
#     This endpoint returns a list of public Datastreams and Datastreams owned by the authenticated user if there is one
#     associated with the given Thing ID.
#     """
#
#     check_thing_by_id(
#         user=request.authenticated_user,
#         thing_id=thing_id,
#         raise_http_errors=True
#     )
#
#     datastream_query, _ = query_datastreams(
#         user=request.authenticated_user,
#         thing_ids=[thing_id],
#     )
#
#     return [
#         build_datastream_response(datastream) for datastream in datastream_query.all()
#     ]
#
#
# @router.post(
#     '{thing_id}/archive',
#     auth=[JWTAuth(), BasicAuth()],
#     response={
#         201: str,
#         401: str,
#         403: str,
#         404: str
#     }
# )
# def archive_thing(request, data: ThingArchiveBody, thing_id: UUID = Path(...)):
#     """"""
#
#     authenticated_user = request.authenticated_user
#
#     thing = get_thing_by_id(
#         user=authenticated_user,
#         thing_id=thing_id,
#         require_ownership=True,
#         raise_http_errors=True
#     )
#
#     datastream_query, _ = query_datastreams(
#         user=request.authenticated_user,
#         thing_ids=[thing_id]
#     )
#
#     datastreams = datastream_query.select_related('processing_level').select_related('observed_property').all()
#
#     if data.datastreams:
#         datastreams = [
#             datastream for datastream in datastreams if datastream.id in data.datastreams
#         ]
#
#     if authenticated_user.hydroshare_token is None:
#         return 403, 'You have not linked a HydroShare account to your HydroServer account.'
#
#     hydroshare_service = hsclient.HydroShare(
#         client_id=settings.AUTHLIB_OAUTH_CLIENTS['hydroshare']['client_id'],
#         token={
#             'access_token': authenticated_user.hydroshare_token['access_token'],
#             'token_type': authenticated_user.hydroshare_token['token_type'],
#             'scope': authenticated_user.hydroshare_token['scope'],
#             'state': '',
#             'expires_in': authenticated_user.hydroshare_token['expires_in'],
#             'refresh_token': authenticated_user.hydroshare_token['refresh_token']
#         }
#     )
#
#     if thing.hydroshare_archive_resource_id:
#         try:
#             archive_resource = hydroshare_service.resource(thing.hydroshare_archive_resource_id)
#         except (Exception,):  # hsclient just raises a generic exception if the resource doesn't exist.
#             archive_resource = None
#     else:
#         archive_resource = None
#
#     if not archive_resource:
#         archive_resource = create_hydroshare_archive_resource(
#             hydroshare_service=hydroshare_service,
#             resource_title=data.resource_title,
#             resource_abstract=data.resource_abstract,
#             resource_keywords=data.resource_keywords,
#             thing=thing,
#         )
#         set_sharing_status = True
#     else:
#         set_sharing_status = False
#
#     datastream_file_names = []
#     processing_levels = list(set([
#         datastream.processing_level.definition for datastream in datastreams
#     ]))
#
#     with tempfile.TemporaryDirectory() as temp_dir:
#         for processing_level in processing_levels:
#             try:
#                 archive_resource.folder_delete(processing_level)
#             except (Exception,):
#                 pass
#             archive_resource.folder_create(processing_level)
#             os.mkdir(os.path.join(temp_dir, processing_level))
#         for datastream in datastreams:
#             temp_file_name = datastream.observed_property.code
#             temp_file_index = 2
#             while f'{datastream.processing_level.definition}_{temp_file_name}' in datastream_file_names:
#                 temp_file_name = f'{datastream.observed_property.code} - {str(temp_file_index)}'
#                 temp_file_index += 1
#             datastream_file_names.append(f'{datastream.processing_level.definition}_{temp_file_name}')
#             temp_file_name = f'{temp_file_name}.csv'
#             temp_file_path = os.path.join(temp_dir, datastream.processing_level.definition, temp_file_name)
#             with open(temp_file_path, 'w') as csv_file:
#                 for line in generate_csv(datastream):
#                     csv_file.write(line)
#             archive_resource.file_upload(temp_file_path, destination_path=datastream.processing_level.definition)
#
#         if set_sharing_status:
#             try:
#                 archive_resource.set_sharing_status(data.public_resource)
#                 archive_resource.save()
#             except (Exception,):
#                 pass
#
#     return 201, archive_resource.resource_id
