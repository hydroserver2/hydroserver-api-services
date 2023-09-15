from ninja import Router
from typing import List
from uuid import UUID
from django.db import transaction
from django.db.models import Q
from accounts.auth.jwt import JWTAuth
from accounts.auth.basic import BasicAuth
from core.models import Thing, Location, ThingAssociation, Person, Unit, ProcessingLevel, Sensor, ObservedProperty
from .schemas import ThingGetResponse, ThingPostBody, ThingPatchBody, ThingOwnershipPatchBody, ThingPrivacyPatchBody, \
    ThingMetadataGetResponse, LocationFields, ThingFields
from .utils import query_things, get_thing_association, get_thing_by_id

from core.utils.unit import transfer_unit_ownership, unit_to_dict
from core.utils.observed_property import transfer_properties_ownership, observed_property_to_dict
from core.utils.processing_level import transfer_processing_level_ownership, processing_level_to_dict
from core.utils.sensor import transfer_sensor_ownership, sensor_to_dict


router = Router(tags=['Things'])


@router.get(
    '',
    auth=[JWTAuth(), BasicAuth(), lambda *_: True],
    response={
        200: List[ThingGetResponse]
    },
    by_alias=True
)
def get_things(request):
    """
    Get a list of Things

    This endpoint returns a list of public Things and Things owned by the authenticated user if there is one.
    """

    things = query_things(
        user=getattr(request, 'authenticated_user', None)
    )

    return things


@router.get(
    '{thing_id}',
    auth=[JWTAuth(), BasicAuth(), lambda *_: True],
    response={
        200: ThingGetResponse,
        404: str
    },
    by_alias=True
)
def get_thing(request, thing_id: UUID):
    """
    Get details for a Thing

    This endpoint returns details for a Thing given a Thing ID.
    """

    thing = get_thing_by_id(user=request.authenticated_user, thing_id=thing_id)

    if not thing:
        return 404, f'Thing with ID: {thing_id} was not found.'

    return 200, thing


@router.post(
    '',
    auth=[JWTAuth(), BasicAuth()],
    response={
        201: ThingGetResponse,
        401: str,
        500: str
    },
    by_alias=True
)
@transaction.atomic
def create_thing(request, data: ThingPostBody):
    """
    Create a Thing

    This endpoint will create a new Thing owned by the authenticated user and returns the created Thing.
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

    thing = get_thing_by_id(user=request.authenticated_user, thing_id=thing.id)

    if not thing:
        return 500, 'Encountered an unexpected error creating Thing.'

    return 201, thing


@router.patch(
    '{thing_id}',
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
def update_thing(request, thing_id: UUID, data: ThingPatchBody):
    """
    Update a Thing

    This endpoint will update an existing Thing owned by the authenticated user and return the updated Thing.
    """

    thing_association = get_thing_association(user=request.authenticated_user, thing_id=thing_id)

    if thing_association == 404:
        return 404, f'Thing with ID: {thing_id} was not found.'

    elif thing_association == 403:
        return 403, 'You do not have permission to modify this Thing.'

    elif thing_association.owns_thing is False:
        return 403, 'You do not have permission to modify this Thing.'

    thing = thing_association.thing
    location = thing.location

    thing_data = data.dict(include=set(ThingFields.__fields__.keys()), exclude_unset=True)
    location_data = data.dict(include=set(LocationFields.__fields__.keys()), exclude_unset=True)

    if thing_data.get('name'):
        location_data['name'] = f'Location for {thing_data["name"]}'

    for field, value in thing_data.items():
        setattr(thing, field, value)

    thing.save()

    for field, value in location_data.items():
        setattr(location, field, value)

    location.save()

    thing = get_thing_by_id(user=request.authenticated_user, thing_id=thing.id)

    if not thing:
        return 500, 'Encountered an unexpected error updating Thing.'

    return 203, thing


@router.delete(
    '{thing_id}',
    auth=[JWTAuth(), BasicAuth()],
    response={
        204: None,
        401: str,
        403: str,
        404: str,
        500: str
    }
)
@transaction.atomic
def delete_thing(request, thing_id: UUID):
    """
    Delete a Thing

    This endpoint will delete an existing Thing if the authenticated user is the primary owner of the Thing.
    """

    thing_association = get_thing_association(user=request.authenticated_user, thing_id=thing_id)

    if thing_association == 404:
        return 404, f'Thing with ID: {thing_id} was not found.'

    elif thing_association == 403:
        return 403, 'You do not have permission to delete this Thing.'

    elif thing_association.is_primary_owner is False and thing_association.owns_thing is True:
        return 403, 'You do not have permission to delete this Thing. Things must be deleted by the primary owner.'

    elif thing_association.is_primary_owner is False:
        return 403, 'You do not have permission to delete this Thing.'

    try:
        thing_association.thing.location.delete()
    except Exception as e:
        return 500, str(e)

    return 204, None


@router.patch(
    '{thing_id}/ownership',
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
def update_thing_ownership(request, thing_id: UUID, data: ThingOwnershipPatchBody):
    """
    Update a Thing's Ownership

    This endpoint allows a Thing owner to modify the ownership of the Thing for other users. Only one type of
    modification can happen per request. Possible options are "make_owner", "remove_owner", and "transfer_primary".
    """

    authenticated_user_association = get_thing_association(
        user=request.authenticated_user,
        thing_id=thing_id
    )

    if authenticated_user_association == 404:
        return 404, f'Thing with ID: {thing_id} was not found.'

    elif authenticated_user_association == 403:
        return 403, 'You do not have permission to modify this Thing\'s ownership.'

    elif authenticated_user_association.owns_thing is False:
        return 403, 'You do not have permission to modify this Thing\'s ownership.'

    try:
        user = Person.objects.get(email=data.email)
    except Person.DoesNotExist:
        return 404, 'User with the given email not found.'

    if request.authenticated_user == user and authenticated_user_association.is_primary_owner is True:
        return 403, 'Primary owner cannot edit their own ownership.'

    if request.authenticated_user != user and authenticated_user_association.is_primary_owner is False:
        return 403, 'You do not have permission to modify this Thing\'s ownership.'

    thing_association, created = ThingAssociation.objects.get_or_create(
        thing=authenticated_user_association.thing, person=user
    )

    if data.transfer_primary:
        if not authenticated_user_association.is_primary_owner:
            return 403, 'Only primary owner can transfer primary ownership.'
        datastreams = authenticated_user_association.thing.datastreams.all()
        for datastream in datastreams:
            transfer_properties_ownership(datastream, user, request.authenticated_user)
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

    thing = get_thing_by_id(user=request.authenticated_user, thing_id=authenticated_user_association.thing.id)

    if not thing:
        return 500, 'Encountered an unexpected error updating Thing ownership.'

    return 203, thing


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
def update_thing_privacy(request, thing_id: UUID, data: ThingPrivacyPatchBody):
    """
    Update a Thing's Privacy

    This endpoint allows the owner of a Thing to toggle it between a private and public resource.
    """

    thing_association = get_thing_association(
        user=request.authenticated_user,
        thing_id=thing_id
    )

    if thing_association == 404:
        return 404, f'Thing with ID: {thing_id} was not found.'

    elif thing_association == 403:
        return 403, 'You do not have permission to modify this Thing\'s privacy.'

    elif thing_association.owns_thing is False:
        return 403, 'You do not have permission to modify this Thing\'s privacy.'

    thing_association.thing.is_private = data.is_private

    if data.is_private:
        thing_associations = ThingAssociation.objects.filter(thing=thing_association.thing)
        for thing_association in thing_associations:
            if thing_association.follows_thing:
                thing_association.delete()

    thing_association.thing.save()

    thing = get_thing_by_id(user=request.authenticated_user, thing_id=thing_association.thing.id)

    if not thing:
        return 500, 'Encountered an unexpected error updating Thing privacy.'

    return 203, thing


@router.patch(
    '{thing_id}/followership',
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
def update_thing_followership(request, thing_id: UUID):
    """
    Update a Thing's Follower Status

    This endpoint allows a user to follow or unfollow a public Thing. Users cannot follow Things they own.
    """

    authenticated_user_association = get_thing_association(
        user=request.authenticated_user,
        thing_id=thing_id
    )

    if authenticated_user_association == 404:
        return 404, f'Thing with ID: {thing_id} was not found.'

    elif authenticated_user_association == 403:
        ThingAssociation.objects.create(
            thing_id=thing_id,
            person=request.authenticated_user,
            follows_thing=True
        )

    elif authenticated_user_association.owns_thing is True:
        return 403, 'Owners cannot update follow status.'

    else:
        authenticated_user_association.delete()

    thing = get_thing_by_id(
        user=request.authenticated_user,
        thing_id=thing_id
    )

    if not thing:
        return 500, 'Encountered an unexpected error updating Thing follower status.'

    return 203, thing


@router.get(
    '{thing_id}/metadata',
    auth=[JWTAuth(), BasicAuth()],
    response={
        200: ThingMetadataGetResponse,
        401: str,
        403: str,
        404: str
    },
    by_alias=True
)
def get_thing_metadata(request, thing_id: UUID):
    """
    Get metadata for a Thing

    This endpoint returns all metadata objects used for a given Thing. The metadata properties returned include
    units, observed properties, sensors, and processing levels.
    """

    thing_association = get_thing_association(user=request.authenticated_user, thing_id=thing_id)

    if thing_association == 404:
        return 404, f'Thing with ID: {thing_id} was not found.'

    elif thing_association == 403:
        return 403, 'You do not have permission to view this Thing\'s metadata.'

    elif thing_association.owns_thing is False:
        return 403, 'You do not have permission to view this Thing\'s metadata.'

    if thing_association.is_primary_owner:
        primary_owner = request.authenticated_user
    else:
        try:
            primary_owner = Person.objects.get(
                thing_associations__thing_id=thing_id,
                thing_associations__is_primary_owner=True
            )
        except Person.DoesNotExist:
            return 404, 'Primary owner cannot be found for this thing.'

    units = Unit.objects.filter(Q(person=primary_owner) | Q(person__isnull=True))
    sensors = Sensor.objects.filter(Q(person=primary_owner))
    processing_levels = ProcessingLevel.objects.filter(Q(person=primary_owner) | Q(person__isnull=True))
    observed_properties = ObservedProperty.objects.filter(Q(person=primary_owner))

    unit_data = [unit_to_dict(unit) for unit in units]
    sensor_data = [sensor_to_dict(sensor) for sensor in sensors]
    processing_level_data = [processing_level_to_dict(pl) for pl in processing_levels]
    observed_property_data = [observed_property_to_dict(op) for op in observed_properties]

    return 200, {
        'units': unit_data,
        'sensors': sensor_data,
        'processing_levels': processing_level_data,
        'observed_properties': observed_property_data
    }
