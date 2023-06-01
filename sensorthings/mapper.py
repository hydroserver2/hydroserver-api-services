from typing import Optional, Callable, List, Union


class MappedField:

    def __init__(
            self,
            field_path: List[Union[str, int]],
            transformation: Optional[Callable] = None,
            linked_component: Union[str, None] = None
    ):
        self.field_path = field_path
        self.transformation = transformation
        self.linked_component = linked_component


class ComponentMap:

    def __init__(self, ref):
        self.ref = ref
        self.__field_maps__ = [
            getattr(self, attr) for attr in dir(self) if isinstance(getattr(self, attr), FieldMap)
        ]

    def get_output_field_map(self, input_delimiter: Optional[str] = None, output_delimiter: Optional[str] = None):
        return {
            input_delimiter.join(field_map.input_field.field_path) if input_delimiter is not None
            else field_map.input_field.field_path: output_delimiter.join(field_map.output_field.field_path)
            if output_delimiter is not None and hasattr(field_map.output_field, 'field_path')
            else getattr(field_map.output_field, 'field_path', None)
            for field_map in self.__field_maps__ if hasattr(field_map.input_field, 'field_path')
        }

    def get_input_field_map(self, input_delimiter: Optional[str] = None, output_delimiter: Optional[str] = None):
        return {
            output_delimiter.join(field_map.output_field.field_path) if output_delimiter is not None
            else field_map.output_field.field_path: input_delimiter.join(field_map.input_field.field_path)
            if input_delimiter is not None and hasattr(field_map.input_field, 'field_path')
            else getattr(field_map.input_field, 'field_path', None)
            for field_map in self.__field_maps__ if hasattr(field_map.output_field, 'field_path')
        }

    def get_output_paths(
            self,
            input_paths: Optional[List[List[str]]] = None,
            delimiter: Optional[str] = None
    ):
        return [
            delimiter.join(field_map.output_field.field_path) if delimiter is not None
            else field_map.output_field.field_path
            for field_map in self.__field_maps__ if hasattr(field_map.output_field, 'field_path')
            and (
                input_paths is None
                or any(
                    field_map.input_field.field_path[:len(input_path)] == input_path for input_path in input_paths
                )
            ) and field_map.output_field.field_path
        ]

    def get_output_components(
            self,
            input_paths: Optional[List[List[str]]] = None,
            prefix: Optional[str] = '',
            delimiter: Optional[str] = None
    ):
        return [
            {
                'component': field_map.output_field.linked_component,
                'prefetch_filter': prefix + delimiter.join(field_map.output_field.field_path + ['id']),
                'prefetch_field': self.ref + '_id',
                'query_structure': {
                    'component': field_map.output_field.linked_component,
                    'array': True
                } if delimiter is not None else field_map.output_field.field_path + ['id', 'in']
            } for field_map in self.__field_maps__ if hasattr(field_map.output_field, 'field_path')
            and field_map.output_field.linked_component is not None
            and (
                input_paths is None
                or any(
                    field_map.input_field.field_path[:len(input_path)] == input_path for input_path in input_paths
                )
            )
        ]

    def get_input_paths(self, output_paths: List[List[str]] = None):
        return [
            field_map.input_field.field_path for field_map
            in self.__field_maps__ if hasattr(field_map.input_field, 'field_path')
            and (
                output_paths is None
                or any(
                    field_map.output_field.field_path[:len(output_path)] == output_path for output_path in output_paths
                )
            )
        ]


class FieldMap:

    def __init__(self, input_field: Optional[MappedField] = None, output_field: Optional[MappedField] = None):
        self.input_field = input_field
        self.output_field = output_field


class ThingAssociation(ComponentMap):

    id = FieldMap(
        MappedField(['id']),
        MappedField(['id'])
    )

    thing_id = FieldMap(
        MappedField(['thing_id']),
        MappedField(['thing_id'])
    )

    person_id = FieldMap(
        MappedField(['id']),
        MappedField(['person', 'id'])
    )

    first_name = FieldMap(
        MappedField(['firstName']),
        MappedField(['person', 'first_name'])
    )

    last_name = FieldMap(
        MappedField(['lastName']),
        MappedField(['person', 'last_name'])
    )

    email = FieldMap(
        MappedField(['email']),
        MappedField(['person', 'email'])
    )

    organization = FieldMap(
        MappedField(['organization']),
        MappedField(['person', 'organization'])
    )

    phone = FieldMap(
        MappedField(['phone']),
        MappedField(['person', 'phone'])
    )


class Thing(ComponentMap):

    id = FieldMap(
        MappedField(['id']),
        MappedField(['id'])
    )

    name = FieldMap(
        MappedField(['name']),
        MappedField(['name'])
    )

    description = FieldMap(
        MappedField(['description']),
        MappedField(['description'])
    )

    sampling_feature_code = FieldMap(
        MappedField(['properties', 'samplingFeatureCode']),
        MappedField(['sampling_feature_code'])
    )

    sampling_feature_type = FieldMap(
        MappedField(['properties', 'samplingFeatureType']),
        MappedField(['sampling_feature_type'])
    )

    site_type = FieldMap(
        MappedField(['properties', 'siteType']),
        MappedField(['site_type'])
    )

    contact_people = FieldMap(
        MappedField(['properties', 'contactPeople']),
        MappedField([], linked_component='ThingAssociation')
    )


class Location(ComponentMap):

    id = FieldMap(
        MappedField(['id']),
        MappedField(['thing_id'])
    )

    name = FieldMap(
        MappedField(['name']),
        MappedField(['name'])
    )

    description = FieldMap(
        MappedField(['description']),
        MappedField(['description'])
    )

    encoding_type = FieldMap(
        MappedField(['encodingType']),
        MappedField(['encoding_type'])
    )

    latitude = FieldMap(
        MappedField(['location', 'geometry', 'coordinates'], transformation=lambda v, m: [v, m.longitude]),
        MappedField(['latitude'], transformation=lambda v, m: v[0])
    )

    longitude = FieldMap(
        MappedField(['location', 'geometry', 'coordinates'], transformation=lambda v, m: [m.latitude, v]),
        MappedField(['longitude'], transformation=lambda v, m: v[1])
    )

    location_type = FieldMap(
        MappedField(['location', 'type'], transformation=lambda: 'Feature')
    )

    geometry_type = FieldMap(
        MappedField(['location', 'geometry', 'type'], transformation=lambda: 'Point')
    )

    city = FieldMap(
        MappedField(['properties', 'city']),
        MappedField(['city'])
    )

    state = FieldMap(
        MappedField(['properties', 'state']),
        MappedField(['state'])
    )

    county = FieldMap(
        MappedField(['properties', 'county']),
        MappedField(['county'])
    )

    elevation = FieldMap(
        MappedField(['properties', 'elevation']),
        MappedField(['elevation'])
    )

    elevation_datum = FieldMap(
        MappedField(['properties', 'elevationDatum']),
        MappedField(['elevation_datum'])
    )


class Sensor(ComponentMap):

    id = FieldMap(
        MappedField(['id']),
        MappedField(['id'])
    )

    name = FieldMap(
        MappedField(['name']),
        MappedField(['name'])
    )

    description = FieldMap(
        MappedField(['description']),
        MappedField(['description'])
    )

    encoding_type = FieldMap(
        MappedField(['encoding_type']),
        MappedField(['encoding_type'])
    )

    method_code = FieldMap(
        MappedField(['metadata', 'methodCode']),
        MappedField(['method_code'])
    )

    method_type = FieldMap(
        MappedField(['metadata', 'methodType']),
        MappedField(['method_type'])
    )

    method_link = FieldMap(
        MappedField(['metadata', 'methodLink']),
        MappedField(['method_link'])
    )

    manufacturer = FieldMap(
        MappedField(['metadata', 'sensorModel', 'sensorManufacturer']),
        MappedField(['manufacturer'])
    )

    model = FieldMap(
        MappedField(['metadata', 'sensorModel', 'sensorModelName']),
        MappedField(['model'])
    )

    model_url = FieldMap(
        MappedField(['metadata', 'sensorModel', 'sensorModelURL']),
        MappedField(['model_url'])
    )


class ObservedProperty(ComponentMap):

    id = FieldMap(
        MappedField(['id']),
        MappedField(['id'])
    )

    name = FieldMap(
        MappedField(['name']),
        MappedField(['name'])
    )

    definition = FieldMap(
        MappedField(['definition']),
        MappedField(['definition'])
    )

    description = FieldMap(
        MappedField(['description']),
        MappedField(['description'])
    )

    variable_code = FieldMap(
        MappedField(['metadata', 'variableCode']),
        MappedField(['variable_code'])
    )

    variable_type = FieldMap(
        MappedField(['metadata', 'variableType']),
        MappedField(['variable_type'])
    )


class Datastream(ComponentMap):

    id = FieldMap(
        MappedField(['id']),
        MappedField(['id'])
    )

    observed_property_id = FieldMap(
        MappedField(['observed_property_id']),
        MappedField(['observed_property_id'])
    )

    sensor_id = FieldMap(
        MappedField(['sensor_id']),
        MappedField(['sensor_id'])
    )

    thing_id = FieldMap(
        MappedField(['thing_id']),
        MappedField(['thing_id'])
    )

    name = FieldMap(
        MappedField(['name']),
        MappedField(['name'])
    )

    description = FieldMap(
        MappedField(['description']),
        MappedField(['description'])
    )

    unit_name = FieldMap(
        MappedField(['unitOfMeasurement', 'name']),
        MappedField(['unit', 'name'])
    )

    unit_definition = FieldMap(
        MappedField(['unitOfMeasurement', 'definition']),
        MappedField(['unit', 'definition'])
    )

    unit_symbol = FieldMap(
        MappedField(['unitOfMeasurement', 'symbol']),
        MappedField(['unit', 'symbol'])
    )

    observation_type = FieldMap(
        MappedField(['observationType']),
        MappedField(['observation_type'])
    )

    result_type = FieldMap(
        MappedField(['properties', 'resultType']),
        MappedField(['result_type'])
    )

    status = FieldMap(
        MappedField(['properties', 'status']),
        MappedField(['status'])
    )

    sampled_medium = FieldMap(
        MappedField(['properties', 'sampledMedium']),
        MappedField(['sampled_medium'])
    )

    value_count = FieldMap(
        MappedField(['properties', 'valueCount']),
        MappedField(['value_count'])
    )

    no_data_value = FieldMap(
        MappedField(['properties', 'noDataValue']),
        MappedField(['no_data_value'])
    )

    processing_level_code = FieldMap(
        MappedField(['properties', 'processingLevelCode']),
        MappedField(['processing_level', 'processing_level_code'])
    )

    intended_time_spacing = FieldMap(
        MappedField(['properties', 'intendedTimeSpacing']),
        MappedField(['intended_time_spacing'])
    )

    intended_time_spacing_unit_name = FieldMap(
        MappedField(['properties', 'intendedTimeSpacingUnitOfMeasurement', 'name']),
        MappedField(['intended_time_spacing_units', 'name'])
    )

    intended_time_spacing_unit_definition = FieldMap(
        MappedField(['properties', 'intendedTimeSpacingUnitOfMeasurement', 'definition']),
        MappedField(['intended_time_spacing_units', 'definition'])
    )

    intended_time_spacing_unit_symbol = FieldMap(
        MappedField(['properties', 'intendedTimeSpacingUnitOfMeasurement', 'symbol']),
        MappedField(['intended_time_spacing_units', 'symbol'])
    )

    aggregation_statistic = FieldMap(
        MappedField(['properties', 'aggregationStatistic']),
        MappedField(['aggregation_statistic'])
    )

    time_aggregation_interval = FieldMap(
        MappedField(['properties', 'timeAggregationInterval']),
        MappedField(['time_aggregation_interval'])
    )

    time_aggregation_interval_unit_name = FieldMap(
        MappedField(['properties', 'timeAggregationIntervalUnitOfMeasurement', 'name']),
        MappedField(['time_aggregation_interval_units', 'name'])
    )

    time_aggregation_interval_unit_definition = FieldMap(
        MappedField(['properties', 'timeAggregationIntervalUnitOfMeasurement', 'definition']),
        MappedField(['time_aggregation_interval_units', 'definition'])
    )

    time_aggregation_interval_unit_symbol = FieldMap(
        MappedField(['properties', 'timeAggregationIntervalUnitOfMeasurement', 'symbol']),
        MappedField(['time_aggregation_interval_units', 'symbol'])
    )

    phenomenon_start_time = FieldMap(
        MappedField(['properties', 'phenomenonTime'], transformation=lambda v, m: f'{v}/{m.phenomenon_end_time}'),
        MappedField(['phenomenon_start_time'], transformation=lambda v, m: v.split('/')[0])
    )

    phenomenon_end_time = FieldMap(
        MappedField(['properties', 'phenomenonTime'], transformation=lambda v, m: f'{m.phenomenon_start_time}/{v}'),
        MappedField(['phenomenon_end_time'], transformation=lambda v, m: v.split('/')[1])
    )

    result_begin_time = FieldMap(
        MappedField(['properties', 'resultTime'], transformation=lambda v, m: f'{v}/{m.result_end_time}'),
        MappedField(['result_begin_time'], transformation=lambda v, m: v.split('/')[0])
    )

    result_end_time = FieldMap(
        MappedField(['properties', 'resultTime'], transformation=lambda v, m: f'{m.result_begin_time}/{v}'),
        MappedField(['result_end_time'], transformation=lambda v, m: v.split('/')[1])
    )


class Observation(ComponentMap):

    id = FieldMap(
        MappedField(['id']),
        MappedField(['id'])
    )

    datastream_id = FieldMap(
        MappedField(['datastream_id']),
        MappedField(['datastream_id'])
    )

    result = FieldMap(
        MappedField(['result']),
        MappedField(['result'])
    )

    result_time = FieldMap(
        MappedField(['resultTime']),
        MappedField(['result_time'])
    )

    result_quality = FieldMap(
        MappedField(['resultQuality']),
        MappedField(['result_quality'])
    )

    phenomenon_time = FieldMap(
        MappedField(['phenomenonTime']),
        MappedField(['phenomenon_time'])
    )

    valid_begin_time = FieldMap(
        MappedField(['properties', 'validTime'], transformation=lambda v, m: f'{v}/{m.valid_end_time}'),
        MappedField(['valid_begin_time'], transformation=lambda v, m: v.split('/')[0])
    )

    valid_end_time = FieldMap(
        MappedField(['properties', 'validTime'], transformation=lambda v, m: f'{m.valid_begin_time}/{v}'),
        MappedField(['valid_begin_time'], transformation=lambda v, m: v.split('/')[1])
    )


sensorthings_mapper = {
    'ThingAssociation': ThingAssociation(ref='thing_association'),
    'Thing': Thing(ref='thing'),
    'Location': Location(ref='location'),
    'Sensor': Sensor(ref='sensor'),
    'ObservedProperty': ObservedProperty(ref='observed_property'),
    'Datastream': Datastream(ref='datastream'),
    'Observation': Observation(ref='observation')
}
