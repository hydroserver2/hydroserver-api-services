from core.models import Unit
import copy


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


def unit_to_dict(unit):
    return {
        "id": unit.pk,
        "name": unit.name,
        "symbol": unit.symbol,
        "definition": unit.definition,
        "unit_type": unit.unit_type,
        "person_id": unit.person.pk if unit.person else None
    }
