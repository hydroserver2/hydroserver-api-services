import copy
import uuid
from django.db.models import Q
from sites.models import Thing, ThingAssociation, ObservedProperty, ProcessingLevel, Unit, Sensor


def build_thing_ownership_fields(thing_associations, authenticated_user):
    is_primary_owner = False
    owner = False
    follows = False

    for thing_association in thing_associations:
        if authenticated_user and thing_association.get('person__email') == authenticated_user.username:
            if thing_association.get('is_primary_owner'):
                is_primary_owner = True
            if thing_association.get('owns_thing'):
                owner = True
            if thing_association.get('follows_thing'):
                follows = True

    return {
        'is_primary_owner': is_primary_owner,
        'owns_thing': owner,
        'follows_thing': follows,
        'owners': thing_associations
    }


def build_things_query(thing_id=None, authenticated_user=None, require_ownership=False):
    """"""

    if authenticated_user:
        owned_things = ThingAssociation.objects.filter(person=authenticated_user).values('thing', flat=True)
    else:
        owned_things = []

    if require_ownership:
        thing_query = Thing.objects.filter(Q(id__in=owned_things))
    else:
        thing_query = Thing.objects.filter(Q(is_private=False) | Q(id__in=owned_things))

    if thing_id:
        thing_query = thing_query.filter(Q(id=thing_id))

    return thing_query


def query_things(thing_id=None, authenticated_user=None):
    """"""

    thing_query = build_things_query(thing_id=thing_id, authenticated_user=authenticated_user)

    things = thing_query.values(
        'id', 'name', 'description', 'sampling_feature_type', 'sampling_feature_code', 'site_type', 'is_private',
        'location__latitude', 'location__longitude', 'location__elevation', 'location__state', 'location__county',
        'location__city'
    )

    thing_associations = ThingAssociation.objects.filter(thing__id__in=[thing['id'] for thing in things]).values(
        'thing_id', 'person__first_name', 'person__last_name', 'person__organization', 'person__email',
        'is_primary_owner', 'owns_thing', 'follows_thing'
    )

    thing_associations_dict = {}
    for thing_association in thing_associations:
        thing_associations_dict.setdefault(thing_association['thing_id'], []).append(thing_association)

    return [
        {
            **build_thing_ownership_fields(
                thing_associations=thing_associations_dict.get(thing['id'], []),
                authenticated_user=authenticated_user
            ),
            **thing
        } for thing in things
    ]


def photo_to_dict(photo):
    return {
        'id': photo.id,
        'thing_id': photo.thing.id,
        'url': photo.url
    }


def transfer_properties_ownership(datastream, new_owner, old_owner):
    """
    Transfers ownership of a datastream's observed property from the old owner to the new owner.
    Checks if the old owner is assigned and correct, then searches for a matching property in
    the new owner's properties. If found, assigns this property to the datastream. If not found,
    creates a new property for the datastream. This way each owner keeps their own list of unique properties
    """
    if datastream.observed_property.person != old_owner or datastream.observed_property.person is None:
        return

    fields_to_compare = ['name', 'definition', 'description', 'variable_type', 'variable_code']
    same_properties = ObservedProperty.objects.filter(
        person=new_owner,
        **{f: getattr(datastream.observed_property, f) for f in fields_to_compare}
    )

    if same_properties.exists():
        datastream.observed_property = same_properties[0]
    else:
        new_property = copy.copy(datastream.observed_property)
        new_property.id = uuid.uuid4()
        new_property.person = new_owner
        new_property.save()
        datastream.observed_property = new_property

    datastream.save()


def transfer_processing_level_ownership(datastream, new_owner, old_owner):
    """
    Transfers ownership of a datastream's processing level from the old owner to the new owner.
    """
    if datastream.processing_level.person != old_owner or datastream.processing_level.person is None:
        return

    fields_to_compare = ['processing_level_code', 'definition', 'explanation']
    same_properties = ProcessingLevel.objects.filter(
        person=new_owner,
        **{f: getattr(datastream.processing_level, f) for f in fields_to_compare}
    )

    if same_properties.exists():
        datastream.processing_level = same_properties[0]
    else:
        new_property = copy.copy(datastream.processing_level)
        new_property.id = None  # Set to None so Django can auto-generate a new unique integer id
        new_property.person = new_owner
        new_property.save()
        datastream.processing_level = new_property

    datastream.save()


def transfer_unit_ownership(datastream, new_owner, old_owner):
    """
    Transfers ownership of a datastream's unit from the old owner to the new owner.
    """
    if datastream.unit.person != old_owner or datastream.unit.person is None:
        return

    fields_to_compare = ['name', 'symbol', 'definition', 'unit_type']

    same_properties = Unit.objects.filter(
        person=new_owner,
        **{f: getattr(datastream.unit, f) for f in fields_to_compare}
    )

    if same_properties.exists():
        datastream.unit = same_properties[0]
    else:
        new_property = copy.copy(datastream.unit)
        new_property.id = None  # Set to None so Django can auto-generate a new unique integer id
        new_property.person = new_owner
        new_property.save()
        datastream.unit = new_property

    datastream.save()


def transfer_sensor_ownership(datastream, new_owner, old_owner):
    """
    Transfers ownership of a datastream's sensor from the old owner to the new owner.
    """
    if datastream.sensor.person != old_owner or datastream.sensor.person is None:
        return

    fields_to_compare = ['name', 'description', 'encoding_type', 'manufacturer', 'model', 'model_url',
                         'method_type', 'method_link', 'method_code']

    same_properties = Sensor.objects.filter(
        person=new_owner,
        **{f: getattr(datastream.sensor, f) for f in fields_to_compare}
    )

    if same_properties.exists():
        datastream.sensor = same_properties[0]
    else:
        new_property = copy.copy(datastream.sensor)
        new_property.id = uuid.uuid4()
        new_property.person = new_owner
        new_property.save()
        datastream.sensor = new_property

    datastream.save()
