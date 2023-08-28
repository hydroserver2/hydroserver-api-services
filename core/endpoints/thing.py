from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from ninja import Router, Schema

from accounts.models import CustomUser
from core.models import ThingAssociation, Thing, Location, Sensor, Unit, ProcessingLevel, ObservedProperty
from core.utils.unit import transfer_unit_ownership, unit_to_dict
from core.utils.observed_property import transfer_properties_ownership, observed_property_to_dict
from core.utils.processing_level import transfer_processing_level_ownership, processing_level_to_dict
from core.utils.sensor import transfer_sensor_ownership, sensor_to_dict
from core.utils.authentication import jwt_auth, jwt_check_user, thing_ownership_required
from core.utils.thing import thing_to_dict

router = Router(tags=['Things'])


class ThingInput(Schema):
    name: str
    description: str = None
    sampling_feature_type: str = None
    sampling_feature_code: str = None
    site_type: str = None
    include_data_disclaimer: bool = False
    data_disclaimer: str = None
    latitude: float
    longitude: float
    elevation: float
    state: str = None
    county: str = None


@router.post('', auth=jwt_auth)
def create_thing(request, data: ThingInput):
    with transaction.atomic():
        new_thing = Thing.objects.create(name=data.name,
                                         description=data.description,
                                         sampling_feature_type=data.sampling_feature_type,
                                         sampling_feature_code=data.sampling_feature_code,
                                         site_type=data.site_type, 
                                         include_data_disclaimer=data.include_data_disclaimer, 
                                         data_disclaimer=data.data_disclaimer if data.include_data_disclaimer else None)

        Location.objects.create(name='Location for ' + new_thing.name,
                                description='location',
                                encoding_type="application/geo+json",
                                latitude=data.latitude, longitude=data.longitude, elevation=data.elevation,
                                state=data.state,
                                county=data.county,
                                thing=new_thing)

        ThingAssociation.objects.create(thing=new_thing, person=request.authenticated_user,
                                        owns_thing=True, is_primary_owner=True)

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



class UpdateThingInput(Schema):
    name: str = None
    description: str = None
    sampling_feature_type: str = None
    sampling_feature_code: str = None
    site_type: str = None
    include_data_disclaimer: bool = False
    data_disclaimer: str = None
    latitude: float = None
    longitude: float = None
    elevation: float = None
    city: str = None
    state: str = None
    county: str = None


@router.patch('/{thing_id}')
@thing_ownership_required
def update_thing(request, thing_id: str, data: UpdateThingInput):
    thing = request.thing
    location = Location.objects.get(thing=thing)

    if data.name is not None:
        thing.name = data.name
        location.name = 'Location for ' + data.name
    if data.description is not None:
        thing.description = data.description
    if data.sampling_feature_type is not None:
        thing.sampling_feature_type = data.sampling_feature_type
    if data.sampling_feature_code is not None:
        thing.sampling_feature_code = data.sampling_feature_code
    if data.site_type is not None:
        thing.site_type = data.site_type
    if data.include_data_disclaimer is not None:
        thing.include_data_disclaimer = data.include_data_disclaimer
    if data.data_disclaimer is not None:
        thing.data_disclaimer = data.data_disclaimer

    if data.latitude is not None:
        location.latitude = data.latitude
    if data.longitude is not None:
        location.longitude = data.longitude
    if data.elevation is not None:
        location.elevation = data.elevation
    if data.city is not None:
        location.city = data.city
    if data.state is not None:
        location.state = data.state
    if data.county is not None:
        location.county = data.county

    thing.save()
    location.save()

    return JsonResponse(thing_to_dict(thing, request.authenticated_user), status=200)


@router.delete('/{thing_id}')
@thing_ownership_required
def delete_thing(request, thing_id: str):
    try:
        request.thing.delete()
    except Exception as e:
        return JsonResponse(status=500, detail=str(e))

    return JsonResponse({'detail': 'Site deleted successfully.'}, status=200)


class UpdateOwnershipInput(Schema):
    email: str
    make_owner: bool = False
    remove_owner: bool = False
    transfer_primary: bool = False


@router.patch('/{thing_id}/ownership', auth=jwt_auth)
@thing_ownership_required
@transaction.atomic
def update_thing_ownership(request, thing_id: str, data: UpdateOwnershipInput):
    flags = [data.make_owner, data.remove_owner, data.transfer_primary]
    if sum(flag is True for flag in flags) != 1:
        return JsonResponse(
            {"error": "Only one action (make_owner, remove_owner, transfer_primary) should be true."}, status=400)

    try:
        user = CustomUser.objects.get(email=data.email)
    except CustomUser.DoesNotExist:
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
    is_private: bool


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
    units = Unit.objects.filter(Q(person=primary_owner) | Q(person__isnull=True))
    sensors = Sensor.objects.filter(Q(person=primary_owner))
    processing_levels = ProcessingLevel.objects.filter(Q(person=primary_owner) | Q(person__isnull=True))
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
