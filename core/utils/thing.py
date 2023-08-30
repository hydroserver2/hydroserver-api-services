from core.models import ThingAssociation


def thing_to_dict(thing, user):
    thing_dict = {
        "id": thing.pk,
        "name": thing.name,
        "description": thing.description,
        "sampling_feature_type": thing.sampling_feature_type,
        "sampling_feature_code": thing.sampling_feature_code,
        "site_type": thing.site_type,
        "is_private": thing.is_private,
        "include_data_disclaimer": thing.include_data_disclaimer,
        "data_disclaimer": thing.data_disclaimer,
        "latitude": round(float(thing.location.latitude), 6),
        "longitude": round(float(thing.location.longitude), 6),
        "elevation": round(float(thing.location.elevation), 6),
        "state": thing.location.state,
        "county": thing.location.county,
        "is_primary_owner": False,
        "owns_thing": False,
        "follows_thing": False,
        "owners": [],
    }
    thing_associations = ThingAssociation.objects.filter(thing=thing)
    for thing_association in thing_associations:
        person = thing_association.person
        if thing_association.owns_thing:
            thing_dict['owners'].append({
                "firstName": person.first_name,
                "lastName": person.last_name,
                "organizationName": user.organization.name if hasattr(user, 'organization') else None,
                "email": person.email,
                "isPrimaryOwner": thing_association.is_primary_owner
            })
    if user is not None:
        thing_association = thing_associations.filter(person=user).first()
        if thing_association:
            thing_dict.update({
                "is_primary_owner": thing_association.is_primary_owner,
                "owns_thing": thing_association.owns_thing,
                "follows_thing": thing_association.follows_thing,
            })
    return thing_dict


def photo_to_dict(photo):
    return {
        'id': photo.id, 
        'thingId': photo.thing.id, 
        'url': photo.url
        }
