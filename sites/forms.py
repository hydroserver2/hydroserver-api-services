from .models import Thing, ObservedProperty, Sensor, Datastream
from django.forms import ModelForm, FloatField, ChoiceField, Select, ModelChoiceField, TextInput, CharField


class ThingForm(ModelForm):
    latitude = FloatField(widget=TextInput(attrs={'id': 'id_latitude'}))
    longitude = FloatField(widget=TextInput(attrs={'id': 'id_longitude'}))
    elevation = FloatField(widget=TextInput(attrs={'id': 'id_elevation'}))
    city = CharField(widget=TextInput(attrs={'id': 'id_nearest_town'}))
    state = CharField(widget=TextInput(attrs={'id': 'id_state'}))
    country = CharField(widget=TextInput(attrs={'id': 'id_country'}))

    class Meta:
        model = Thing
        fields = ['name', 'description', 'latitude', 'longitude', 'elevation', 'city', 'state', 'country']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        thing = kwargs.get('instance')
        if thing:
            for field in ['latitude', 'longitude', 'elevation', 'city', 'state', 'country']:
                self.fields[field].initial = getattr(thing.location, field)


class DatastreamForm(ModelForm):
    method = ModelChoiceField(queryset=Sensor.objects.none(),
                              widget=Select(attrs={'class': 'form-control', 'id': 'id_method_select'}))

    allowed_sample_medium = ['Air', 'Soil', 'Sediment', 'Liquid aqueous', 'Equipment', 'Not applicable', 'Other']
    sampled_medium = ChoiceField(label='Sampled Medium',
                                       choices=[(medium, medium) for medium in allowed_sample_medium],
                                       widget=Select(attrs={'class': 'form-control'}))
    allowed_units = ['Degrees Celsius', 'Degrees Fahrenheit', 'Feet', 'Meters']
    unit_of_measurement = ChoiceField(label='Unit Of Measurement',
                                      choices=[(unit, unit) for unit in allowed_units],
                                      widget=Select(attrs={'class': 'form-control'}))

    observed_property = ModelChoiceField(queryset=ObservedProperty.objects.all(),
                                         widget=Select(attrs={'class': 'form-control', 'id': 'id_observed_property'}))

    class Meta:
        model = Datastream
        fields = ['method', 'unit_of_measurement']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['method'] = ModelChoiceField(
                queryset=user.sensor_set.all().order_by('manufacturer', 'model', 'method_type'),
                widget=Select(attrs={'class': 'form-control', 'id': 'id_method_select'}))


class SensorSelectionForm(ModelForm):
    sensor = ChoiceField()

    def __init__(self, *args, **kwargs):
        sensors = kwargs.pop('sensors', None)
        super().__init__(*args, **kwargs)
        sensor_choices = [(s.pk, s.name) for s in sensors]
        self.fields['sensor'] = ChoiceField(choices=sensor_choices, widget=Select())

    class Meta:
        model = Sensor
        fields = ['sensor']
