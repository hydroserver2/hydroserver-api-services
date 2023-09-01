from core.models import Sensor
import copy
import uuid


def sensor_to_dict(sensor):
    return {
        "id": sensor.pk,
        "name": sensor.name,
        "description": sensor.description,
        "manufacturer": sensor.manufacturer,
        "model": sensor.model,
        "methodType": sensor.method_type,
        "methodCode": sensor.method_code,
        "methodLink": sensor.method_link,
        "encodingType": sensor.encoding_type,
        "modelLink": sensor.model_link,
    }


def transfer_sensor_ownership(datastream, new_owner, old_owner):
    """
    Transfers ownership of a datastream's sensor from the old owner to the new owner.
    """
    if datastream.sensor.person != old_owner or datastream.sensor.person is None:
        return

    fields_to_compare = ['name', 'description', 'encoding_type', 'manufacturer', 'model', 'model_link',
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
