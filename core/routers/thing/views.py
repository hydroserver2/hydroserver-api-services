from ninja import Router
from typing import List
from uuid import UUID
from django.db import transaction
from django.db.models import Q
from accounts.auth.jwt import JWTAuth
from accounts.auth.basic import BasicAuth
from accounts.auth.anonymous import anonymous_auth
from core.models import Thing, Location, ThingAssociation, Person, Unit, ProcessingLevel, Sensor, ObservedProperty
from .schemas import ThingGetResponse, ThingPostBody, ThingPatchBody, ThingOwnershipPatchBody, ThingPrivacyPatchBody, \
    ThingMetadataGetResponse, LocationFields, ThingFields
from .utils import query_visible_things, query_thing_by_id, build_thing_response

from core.utils.unit import transfer_unit_ownership, unit_to_dict
from core.utils.observed_property import transfer_properties_ownership, observed_property_to_dict
from core.utils.processing_level import transfer_processing_level_ownership, processing_level_to_dict
from core.utils.sensor import transfer_sensor_ownership, sensor_to_dict


router = Router(tags=['Things'])


@router.get(
    '',
    auth=[JWTAuth(), BasicAuth(), anonymous_auth],
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

    user = getattr(request, 'authenticated_user', None)
    things = query_visible_things(user=user)

    return [
        build_thing_response(user, thing) for thing in things
    ]


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

    thing = query_thing_by_id(user=request.authenticated_user, thing_id=thing_id)

    return 200, build_thing_response(request.authenticated_user, thing)


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

    thing = query_thing_by_id(user=request.authenticated_user, thing_id=thing.id)

    return 201, build_thing_response(request.authenticated_user, thing)


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

    thing = query_thing_by_id(user=request.authenticated_user, thing_id=thing_id, require_ownership=True)
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

    thing = query_thing_by_id(user=request.authenticated_user, thing_id=thing.id)

    return 203, build_thing_response(request.authenticated_user, thing)


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

    thing = query_thing_by_id(user=request.authenticated_user, thing_id=thing_id, require_primary_ownership=True)

    try:
        thing.location.delete()
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

    thing = query_thing_by_id(
        user=request.authenticated_user,
        thing_id=thing_id,
        require_ownership=True,
        prefetch_datastreams=True
    )

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

    thing = query_thing_by_id(user=request.authenticated_user, thing_id=authenticated_user_association.thing.id)

    return 203, build_thing_response(request.authenticated_user, thing)


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

    thing = query_thing_by_id(user=request.authenticated_user, thing_id=thing_id, require_ownership=True)

    thing.is_private = data.is_private

    if data.is_private:
        for thing_association in thing.associates:
            if thing_association.follows_thing:
                thing_association.delete()

    thing.save()

    thing = query_thing_by_id(user=request.authenticated_user, thing_id=thing.id)

    return 203, build_thing_response(request.authenticated_user, thing)


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

    thing = query_thing_by_id(user=request.authenticated_user, thing_id=thing_id, require_unaffiliated=True)

    user_association = next(iter([
        associate for associate in thing.associates.all()
        if associate.follows_thing is True and associate.person == request.authenticated_user
    ]), None)

    if user_association:
        user_association.delete()
    else:
        ThingAssociation.objects.create(
            thing_id=thing_id,
            person=request.authenticated_user,
            follows_thing=True
        )

    thing = query_thing_by_id(
        user=request.authenticated_user,
        thing_id=thing_id
    )

    return 203, build_thing_response(request.authenticated_user, thing)


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

    thing = query_thing_by_id(user=request.authenticated_user, thing_id=thing_id, require_ownership=True)

    primary_owner = next(iter([
        associate.person for associate in thing.associates.all()
        if associate.is_primary_owner is True
    ]), None)

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
