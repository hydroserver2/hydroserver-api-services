import json

from accounts.models import Organization
from sensorthings.models import Thing, ObservedProperty, Sensor, Location
from django.forms import ModelForm, FloatField, ChoiceField, Select, ModelChoiceField, TextInput, CharField

from sites.models import SensorManufacturer, SensorModel


class ThingForm(ModelForm):
    latitude = FloatField(required=True, widget=TextInput(attrs={'id': 'id_latitude'}))
    longitude = FloatField(required=True, widget=TextInput(attrs={'id': 'id_longitude'}))
    elevation = FloatField(required=True, widget=TextInput(attrs={'id': 'id_elevation'}))
    nearest_town = CharField(required=True, widget=TextInput(attrs={'id': 'id_nearest_town'}))
    state = CharField(required=True, widget=TextInput(attrs={'id': 'id_state'}))
    country = CharField(required=True, widget=TextInput(attrs={'id': 'id_country'}))
    organizations = ModelChoiceField(queryset=Organization.objects.all(), required=False, widget=Select)

    class Meta:
        model = Thing
        fields = ['name', 'description', 'latitude', 'longitude', 'elevation', 'nearest_town', 'state', 'country',
                  'organizations']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        thing = kwargs.get('instance')
        if thing:
            organization_id = json.loads(thing.properties).get('organization_id', None)
            try:
                thing_organization = Organization.objects.get(pk=organization_id)
                self.fields['organizations'].initial = thing_organization
            except Organization.DoesNotExist:
                pass
            location = Location.objects.filter(things=thing).first()
            properties = json.loads(location.properties) if location.properties and location.properties != 'None' else {}
            coordinates = json.loads(location.location)['geometry']['coordinates'] if location.location else [None, None]
            self.fields['latitude'].initial = coordinates[0]
            self.fields['longitude'].initial = coordinates[1]
            self.fields['elevation'].initial = properties.get('elevation', '')
            self.fields['nearest_town'].initial = properties.get('city', '')
            self.fields['state'].initial = properties.get('state', '')
            self.fields['country'].initial = properties.get('country', '')


class SensorForm(ModelForm):
    sensor_manufacturer = ModelChoiceField(queryset=SensorManufacturer.objects.all(),
                                           widget=Select(attrs={'class': 'form-control', 'id': 'id_sensor_manufacturer'}))
    sensor_model = ModelChoiceField(queryset=SensorModel.objects.all(),
                                    widget=Select(attrs={'class': 'form-control', 'id': 'id_sensor_model'}))

    allowed_sample_medium = ['Air', 'Soil', 'Sediment', 'Liquid aqueous', 'Equipment', 'Not applicable', 'Other']
    sampled_medium = ChoiceField(label='Sampled Medium',
                                       choices=[(medium, medium) for medium in allowed_sample_medium],
                                       widget=Select(attrs={'class': 'form-control'}))
    allowed_units = ['Degrees Celsius', 'Degrees Fahrenheit', 'Feet', 'Meters']
    unit_of_measurement = ChoiceField(label='Unit Of Measurement',
                                       choices=[(unit, unit) for unit in allowed_units],
                                       widget=Select(attrs={'class': 'form-control'}))

    observed_property = ModelChoiceField(queryset=ObservedProperty.objects.all(),
                                         widget=Select(attrs={'class': 'form-control', 'id': 'id_sensor_manufacturer'}))

    def __init__(self, *args, **kwargs):
        datastream = kwargs.pop('datastream', None)
        super().__init__(*args, **kwargs)
        self.fields['sensor_manufacturer'] = ModelChoiceField(queryset=SensorManufacturer.objects.all())
        self.fields['sensor_model'] = ModelChoiceField(queryset=SensorModel.objects.all())
        if datastream:
            sensor_name = datastream.sensor.name
            try:
                sensor_manufacturer = SensorManufacturer.objects.get(name=sensor_name.split(':')[0])
                self.fields['sensor_manufacturer'].initial = sensor_manufacturer
                sensor_model = SensorModel.objects.get(name=sensor_name.split(':')[1], manufacturer=sensor_manufacturer)
                self.fields['sensor_model'].initial = sensor_model
            except (SensorManufacturer.DoesNotExist, SensorModel.DoesNotExist):
                pass
            self.fields['unit_of_measurement'].initial = datastream.unit_of_measurement
            self.fields['observed_property'].initial = datastream.observed_property

    class Meta:
        model = Sensor
        fields = ['sensor_manufacturer', 'sensor_model', 'sampled_medium', 'unit_of_measurement', 'observed_property']
