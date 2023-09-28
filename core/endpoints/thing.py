from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from ninja import Router, Schema
from pydantic import Field

from accounts.models import Person
from core.models import ThingAssociation, Thing, Location, Sensor, Unit, ProcessingLevel, ObservedProperty
from core.utils.unit import transfer_unit_ownership, unit_to_dict
from core.utils.observed_property import transfer_properties_ownership, observed_property_to_dict
from core.utils.processing_level import transfer_processing_level_ownership, processing_level_to_dict
from core.utils.sensor import transfer_sensor_ownership, sensor_to_dict
from core.utils.authentication import jwt_auth, jwt_check_user, thing_ownership_required
from core.utils.thing import thing_to_dict
from sensorthings.validators import allow_partial

router = Router(tags=['Things'])


class ThingFields(Schema):
    name: str
    description: str
    sampling_feature_type: str = Field(alias="samplingFeatureType")
    sampling_feature_code: str = Field(alias="samplingFeatureCode")
    site_type: str = Field(alias="siteType")
    data_disclaimer: str = Field(None, alias="dataDisclaimer")


class LocationFields(Schema):
    latitude: float
    longitude: float
    elevation_m: float = None
    elevation_datum: str = Field(None, alias='elevationDatum')
    state: str = None
    county: str = None


class ThingPostBody(ThingFields, LocationFields):
    pass


@allow_partial
class ThingPatchBody(ThingFields, LocationFields):
    pass


@router.post('', auth=jwt_auth)
@transaction.atomic
def create_thing(request, data: ThingPostBody):
    new_location = Location.objects.create(
        name=f'Location for {data.name}', 
        description='location',
        encoding_type="application/geo+json", 
        **data.dict(include=set(LocationFields.__fields__.keys()))
    )

    thing_data = data.dict(include=set(ThingFields.__fields__.keys()))
    new_thing = Thing.objects.create(location=new_location, **thing_data)

    ThingAssociation.objects.create(
        thing=new_thing, 
        person=request.authenticated_user, 
        owns_thing=True, 
        is_primary_owner=True
    )

    return JsonResponse(thing_to_dict(new_thing, request.authenticated_user))


@router.get('', auth=jwt_check_user)
def get_things(request):
    if request.user_if_there_is_one:
        owned_things = ThingAssociation.objects.filter(
            person=request.user_if_there_is_one).values_list('thing', flat=True)
        things = Thing.objects.filter(Q(is_private=False) | Q(id__in=owned_things))
    else:
        things = Thing.objects.filter(is_private=False)
    return JsonResponse([thing_to_dict(thing, request.user_if_there_is_one) for thing in things], safe=False)


@router.get('/{thing_id}', auth=jwt_check_user)
def get_thing(request, thing_id: str):
    thing = Thing.objects.get(id=thing_id)
    thing_dict = thing_to_dict(thing, request.user_if_there_is_one)
    return JsonResponse(thing_dict)


def update_object_from_data(obj, data_dict):
    for key, value in data_dict.items():
        if value is not None:
            setattr(obj, key, value)


@router.patch('/{thing_id}', by_alias=True)
@thing_ownership_required
@transaction.atomic
def update_thing(request, thing_id: str, data: ThingPatchBody):
    thing = request.thing

    thing_data = data.dict(include=set(ThingFields.__fields__.keys()))
    location_data = data.dict(include=set(LocationFields.__fields__.keys()))

    if thing_data.get("name"):
        location_data["name"] = f'Location for {thing_data["name"]}'

    update_object_from_data(thing, thing_data)
    update_object_from_data(thing.location, location_data)

    thing.save()
    thing.location.save()

    return JsonResponse(thing_to_dict(thing, request.authenticated_user), status=200)


@router.delete('/{thing_id}')
@thing_ownership_required
def delete_thing(request, thing_id: str):
    try:
        request.thing.location.delete()
    except Exception as e:
        return JsonResponse(status=500, detail=str(e))

    return JsonResponse({'detail': 'Site deleted successfully.'}, status=200)


class UpdateOwnershipInput(Schema):
    email: str
    make_owner: bool = Field(False, alias="makeOwner")
    remove_owner: bool = Field(False, alias="removeOwner")
    transfer_primary: bool = Field(False, alias="transferPrimary")


@router.patch('/{thing_id}/ownership', auth=jwt_auth)
@thing_ownership_required
@transaction.atomic
def update_thing_ownership(request, thing_id: str, data: UpdateOwnershipInput):
    flags = [data.make_owner, data.remove_owner, data.transfer_primary]
    if sum(flag is True for flag in flags) != 1:
        return JsonResponse(
            {"error": "Only one action (make_owner, remove_owner, transfer_primary) should be true."}, status=400)

    try:
        user = Person.objects.get(email=data.email)
    except Person.DoesNotExist:
        return JsonResponse({"error": "Specified user not found."}, status=404)

    current_user_association = ThingAssociation.objects.get(thing=request.thing, person=request.authenticated_user)

    if request.authenticated_user == user and current_user_association.is_primary_owner:
        return JsonResponse({"error": "Primary owner cannot edit their own ownership."}, status=403)
    if not current_user_association.is_primary_owner and user != request.authenticated_user:
        return JsonResponse({"error": "NotPrimaryOwner."}, status=403)

    thing_association, created = ThingAssociation.objects.get_or_create(thing=request.thing, person=user)

    if data.transfer_primary:
        if not current_user_association.is_primary_owner:
            return JsonResponse({"error": "Only primary owner can transfer primary ownership."}, status=403)
        datastreams = request.thing.datastreams.all()
        for datastream in datastreams:
            transfer_properties_ownership(datastream, user, request.authenticated_user)
            transfer_processing_level_ownership(datastream, user, request.authenticated_user)
            transfer_unit_ownership(datastream, user, request.authenticated_user)
            transfer_sensor_ownership(datastream, user, request.authenticated_user)
        current_user_association.is_primary_owner = False
        current_user_association.save()
        thing_association.is_primary_owner = True
        thing_association.owns_thing = True
    elif data.remove_owner:
        if thing_association.is_primary_owner:
            return JsonResponse({"error": "Cannot remove primary owner."}, status=400)
        thing_association.delete()
        return JsonResponse(thing_to_dict(request.thing, request.authenticated_user), status=200)
    elif data.make_owner:
        if not created:
            return JsonResponse({"warning": "Specified user is already an owner of this site"}, status=422)
        thing_association.owns_thing = True

    thing_association.follows_thing = False
    thing_association.save()
    return JsonResponse(thing_to_dict(request.thing, request.authenticated_user), status=200)


class UpdateThingPrivacy(Schema):
    is_private: bool = Field(None, alias="isPrivate")


@router.patch('/{thing_id}/privacy', auth=jwt_auth)
@thing_ownership_required
def update_thing_privacy(request, thing_id: str, data: UpdateThingPrivacy):
    thing = request.thing
    thing.is_private = data.is_private
    thing_associations = ThingAssociation.objects.filter(thing=thing)

    if data.is_private:
        for thing_association in thing_associations:
            if thing_association.follows_thing:
                thing_association.delete()

    thing.save()

    return JsonResponse(thing_to_dict(thing, request.authenticated_user))


@router.patch('/{thing_id}/followership', auth=jwt_auth)
def update_thing_followership(request, thing_id: str):
    thing = Thing.objects.get(id=thing_id)

    if request.authenticated_user.thing_associations.filter(thing=thing, owns_thing=True).exists():
        return JsonResponse({"error": "Owners cannot update follow status"}, status=400)

    thing_association, created = ThingAssociation.objects.get_or_create(thing=thing, person=request.authenticated_user)

    if thing_association.follows_thing:
        thing_association.delete()
    else:
        thing_association.follows_thing = True
        thing_association.save()

    return JsonResponse(thing_to_dict(thing, request.authenticated_user))
    

@router.get('/{thing_id}/metadata', auth=jwt_auth)
@thing_ownership_required
def get_primary_owner_metadata(request, thing_id):
    thing_associations = ThingAssociation.objects.filter(thing=request.thing, is_primary_owner=True)
    primary_owner = thing_associations.first().person if thing_associations.exists() else None

    if not primary_owner:
        return JsonResponse({'error': 'Primary owner cannot be found for thing'}, status=401)
    units = Unit.objects.filter(Q(person=primary_owner))
    sensors = Sensor.objects.filter(Q(person=primary_owner))
    processing_levels = ProcessingLevel.objects.filter(Q(person=primary_owner))
    observed_properties = ObservedProperty.objects.filter(Q(person=primary_owner))

    unit_data = [unit_to_dict(unit) for unit in units]
    sensor_data = [sensor_to_dict(sensor) for sensor in sensors]
    processing_level_data = [processing_level_to_dict(pl) for pl in processing_levels]
    observed_property_data = [observed_property_to_dict(op) for op in observed_properties]

    return JsonResponse({
        'units': unit_data,
        'sensors': sensor_data,
        'processing_levels': processing_level_data,
        'observed_properties': observed_property_data
    })
