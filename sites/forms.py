from .models import Thing, ObservedProperty, Sensor, Datastream, Unit, ProcessingLevel
from django.forms import ModelForm, FloatField, ChoiceField, Select, ModelChoiceField, \
    TextInput, CharField, Form, ValidationError


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


def clean_selection(cleaned_data, custom_name, master_list_name, new_input_name):
    master_input = cleaned_data.get(master_list_name, None)
    new_input = cleaned_data.get(new_input_name, None)
    custom_input = cleaned_data.get(custom_name, None)

    # Ensure that only one field is filled
    num_inputs = sum([bool(master_input), bool(new_input), bool(custom_input)])
    if num_inputs > 1:
        raise ValidationError("Please enter only one field")

    # Set the field to the submitted value
    if master_input:
        cleaned_data[custom_name] = master_input
    elif new_input:
        cleaned_data[custom_name] = new_input
    return cleaned_data


class DatastreamForm(ModelForm):
    method = ChoiceField(choices=[])
    observed_property = ModelChoiceField(queryset=ObservedProperty.objects.none(), empty_label='--- Select an existing observed property ---', widget=Select())
    unit = ModelChoiceField(queryset=Unit.objects.none(), empty_label='--- Select an existing Unit ---', widget=Select())
    processing_level = ModelChoiceField(
        queryset=ProcessingLevel.objects.none(), empty_label='--- Select an existing Processing Level ---',
        label='Processing Level', required=False)

    allowed_sample_medium = ['Air', 'Soil', 'Sediment', 'Liquid aqueous', 'Equipment', 'Not applicable', 'Other']
    sampled_medium = ChoiceField(label='Sampled Medium', choices=[(medium, medium) for medium in allowed_sample_medium])

    status_master_list = ChoiceField(choices=[("", "Select status from master list"), ("Active", "Active"),
                                              ("Inactive", "Inactive"), ("Under Maintenance", "Under Maintenance"),
                                            ("Needs Repair", "Needs Repair"), ("Discontinued", "Discontinued")],
                                     label='Status', required=False)
    status_new = CharField(max_length=100, required=False, widget=TextInput(attrs={'placeholder': 'Enter new status...'}))
    status = ChoiceField(choices=[("", "Select status from your list")], label='Status', required=False)

    no_data_value = FloatField(label='No Data Value', required=False)
    # intended_time_spacing = ChoiceField(choices=[("", "Select intended time spacing")], label='Intended Time Spacing',
    #                                     required=False)
    # intended_time_spacing_units = ChoiceField(choices=[("", "Select intended time spacing units")],
    #                                           label='Intended Time Spacing Units', required=False)
    agg_master_list = ChoiceField(choices=[("", "Select stat from master list..."), ("Mean", "Mean"),
                                                      ("Median", "Median"), ("Maximum", "Maximum"),
                                                      ("Minimum", "Minimum"),
                                                      ("Count", "Count"), ("Sum", "Sum")],
                                             label='Aggregation Statistic', required=False)
    aggregation_statistic_new = CharField(max_length=100, required=False,
                                          widget=TextInput(attrs={'placeholder': 'Enter new agg...'}))
    aggregation_statistic = ChoiceField(choices=[("", "Select statistic from your list...")],
                                        label='Aggregation Statistic', required=False)
    # time_aggregation_interval = ChoiceField(choices=[("", "Select time aggregation interval")],
    #                                         label='Time Aggregation Interval', required=False)
    # time_aggregation_interval_units = ChoiceField(choices=[("", "Select time aggregation interval units")],
    #                                               label='Time Aggregation Interval Units', required=False)

    class Meta:
        model = Datastream
        fields = ['method', 'status', 'status_new', 'status_master_list', 'sampled_medium', 'no_data_value', 'processing_level',
                  # 'intended_time_spacing',
                  'aggregation_statistic', 'agg_master_list', 'aggregation_statistic_new',
                  # 'time_aggregation_interval'
                  ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            sensors = self.user.sensor_set.all().order_by('manufacturer', 'model', 'method_type')
            if sensors.exists():
                self.fields['method'].choices = [(sensor.id, str(sensor)) for sensor in sensors]
            else:
                self.fields['method'].choices = [('', '--- No sensors available ---')]

            datastreams = Datastream.objects.filter(sensor__person=self.user)
            if datastreams.exists():
                existing_statuses = [datastream.status for datastream in datastreams if datastream.status]
                unique_statuses = set(existing_statuses)
                self.fields['status'].choices = [("", "Select status from your list")] + [(status, status) for status in
                                                                                          unique_statuses]

            observed_properties = self.user.observedproperty_set.all()
            if observed_properties.exists():
                self.fields['observed_property'].queryset = observed_properties

            units = self.user.unit_set.all()
            if units.exists():
                self.fields['unit'].queryset = units

            processing_levels = self.user.processing_levels.all()
            if processing_levels.exists():
                self.fields['processing_level'].queryset = processing_levels

    def clean(self):
        cleaned_data = super().clean()
        try:
            cleaned_data = clean_selection(cleaned_data, "status", "status_master_list", "status_new")
        except ValidationError as e:
            self.add_error('status', e)

        try:
            cleaned_data = clean_selection(cleaned_data, 'aggregation_statistic', 'agg_master_list',
                                           'aggregation_statistic_new')
        except ValidationError as e:
            self.add_error('aggregation_statistic', e)
        return cleaned_data


class MethodForm(ModelForm):
    allowed_method_type = ['Derivation', 'Estimation', 'Instrument Deployment', 'Observation', 'Simulation', 'Specimen Analysis', 'Unknown']
    method_type = ChoiceField(label='Method Type', choices=[(method, method) for method in allowed_method_type],widget=Select(attrs={'id': 'id_method_type'}))
    manufacturer = CharField(max_length=255, required=False, widget=TextInput(attrs={'id': 'id_manufacturer'}))
    model = CharField(max_length=255, required=False, widget=TextInput(attrs={'id': 'id_model'}))
    name = CharField(required=False, widget=TextInput(attrs={'placeholder': 'Sensor time series', 'id': 'id_method_name'}))
    description = CharField(required=False, widget=TextInput(attrs={'placeholder': 'A time series of observations derived from a sensor', 'id': 'id_method_description'}))
    method_code = CharField(required=False)
    method_link = CharField(required=False)

    class Meta:
        model = Sensor
        fields = ['method_type', 'manufacturer', 'model', 'name', 'description', 'method_code', 'method_link']


class ObservedPropertyForm(ModelForm):
    class Meta:
        model = ObservedProperty
        fields = ['name', 'definition', 'description']
        widgets = {
            'name': TextInput(attrs={'placeholder': 'Enter a name'}),
            'definition': TextInput(attrs={'placeholder': 'Enter a definition'}),
            'description': TextInput(attrs={'placeholder': 'Enter a description'})
        }


class UnitForm(Form):
    name = CharField(max_length=100)
    symbol = CharField(max_length=50)
    definition = CharField()
    unit_type = CharField(max_length=100)

    class Meta:
        fields = ['name', 'symbol', 'definition', 'unit_type']


class ProcessingLevelForm(Form):
    processing_level_code = CharField(max_length=255)
    definition = CharField()
    explanation = CharField()

    class Meta:
        fields = ['processing_level_code', 'definition', 'explanation']


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
