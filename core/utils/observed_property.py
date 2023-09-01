from core.models import ObservedProperty
import copy
import uuid


def observed_property_to_dict(op):
    return {
        "id": op.pk,
        "name": op.name,
        "personId": op.person.pk if op.person else None,
        "definition": op.definition,
        "description": op.description,
        "type": op.type,
        "code": op.code,
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

    fields_to_compare = ['name', 'definition', 'description', 'type', 'code']
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
