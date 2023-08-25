from sites.models import ProcessingLevel
import copy

def processing_level_to_dict(processing_level):
    return {
        "id": processing_level.pk,
        "processing_level_code": processing_level.processing_level_code,
        "definition": processing_level.definition,
        "explanation": processing_level.explanation,
        "person_id": processing_level.person.pk if processing_level.person else None
    }

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