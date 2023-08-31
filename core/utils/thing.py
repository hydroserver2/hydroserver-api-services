from core.models import ThingAssociation


def thing_to_dict(thing, user):
    thing_dict = {
        "id": thing.pk,
        "name": thing.name,
        "description": thing.description,
        "samplingFeatureType": thing.sampling_feature_type,
        "samplingFeatureCode": thing.sampling_feature_code,
        "siteType": thing.site_type,
        "isPrivate": thing.is_private,
        "dataDisclaimer": thing.data_disclaimer,
        "latitude": round(float(thing.location.latitude), 6),
        "longitude": round(float(thing.location.longitude), 6),
        "elevation_m": round(float(thing.location.elevation_m), 6),
        "state": thing.location.state,
        "county": thing.location.county,
        "isPrimaryOwner": False,
        "ownsThing": False,
        "followsThing": False,
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
                "isPrimaryOwner": thing_association.is_primary_owner,
                "ownsThing": thing_association.owns_thing,
                "followsThing": thing_association.follows_thing,
            })
    return thing_dict


def photo_to_dict(photo):
    return {
        'id': photo.id, 
        'thingId': photo.thing.id, 
        'url': photo.url
        }
