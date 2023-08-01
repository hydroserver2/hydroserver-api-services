from hydroloader import HydroLoaderConf
from typing import Optional
from datetime import datetime
from ninja import Schema
from uuid import UUID
from hydrothings.validators import allow_partial

class GetTokenInput(Schema):
    email: str
    password: str


class CreateRefreshInput(Schema):
    refresh_token: str


class PasswordResetInput(Schema):
    email: str


class CreateUserInput(Schema):
    first_name: str
    last_name: str
    email: str
    password: str
    middle_name: str = None
    phone: str = None
    address: str = None
    type: str = None
    organization: str = None


class UpdateUserInput(Schema):
    first_name: str = None
    last_name: str = None
    middle_name: str = None
    phone: str = None
    address: str = None
    organization: str = None
    type: str = None


class ThingInput(Schema):
    name: str
    description: str = None
    sampling_feature_type: str = None
    sampling_feature_code: str = None
    site_type: str = None
    latitude: float
    longitude: float
    elevation: float
    state: str = None
    county: str = None


class UpdateOwnershipInput(Schema):
    email: str
    make_owner: bool = False
    remove_owner: bool = False
    transfer_primary: bool = False


class UpdateThingPrivacy(Schema):
    is_private: bool


class UpdateThingInput(Schema):
    name: str = None
    description: str = None
    sampling_feature_type: str = None
    sampling_feature_code: str = None
    site_type: str = None
    latitude: float = None
    longitude: float = None
    elevation: float = None
    city: str = None
    state: str = None
    county: str = None


class SensorInput(Schema):
    name: str = None
    description: str = None
    encoding_type: str = None
    manufacturer: str = None
    model: str = None
    model_url: str = None
    method_type: str = None
    method_link: str = None
    method_code: str = None


class ObservedPropertyInput(Schema):
    name: str
    definition: str
    description: str
    variable_type: str = None
    variable_code: str = None


class CreateDatastreamInput(Schema):
    thing_id: str
    method_id: str
    observed_property_id: str
    processing_level_id: str = None
    unit_id: str = None

    observation_type: str = None
    result_type: str = None
    status: str = None
    sampled_medium: str = None
    value_count: str = None
    no_data_value: str = None
    intended_time_spacing: str = None
    intended_time_spacing_units: str = None

    aggregation_statistic: str = None
    time_aggregation_interval: str = None
    time_aggregation_interval_units: str = None

    phenomenon_start_time: str = None
    phenomenon_end_time: str = None
    result_begin_time: str = None
    result_end_time: str = None


class UpdateDatastreamInput(Schema):
    unit_id: str = None
    method_id: str = None
    observed_property_id: str = None
    processing_level_id: str = None

    observation_type: str = None
    result_type: str = None
    status: str = None
    sampled_medium: str = None
    value_count: str = None
    no_data_value: str = None
    intended_time_spacing: str = None
    intended_time_spacing_units: str = None

    aggregation_statistic: str = None
    time_aggregation_interval: str = None
    time_aggregation_interval_units: str = None

    phenomenon_start_time: str = None
    phenomenon_end_time: str = None
    result_begin_time: str = None
    result_end_time: str = None
    is_visible: bool = None


class CreateUnitInput(Schema):
    name: str
    symbol: str
    definition: str
    unit_type: str


class UpdateUnitInput(Schema):
    name: str
    symbol: str
    definition: str
    unit_type: str


class ProcessingLevelInput(Schema):
    processing_level_code: str
    definition: str
    explanation: str


class DataLoaderGetResponse(Schema):
    id: UUID
    name: str


class DataLoaderPostBody(Schema):
    name: str


@allow_partial
class DataLoaderPatchBody(Schema):
    name: str


class DataSourceGetResponse(HydroLoaderConf):
    id: UUID
    name: str
    data_loader: Optional[DataLoaderGetResponse]
    data_source_thru: Optional[datetime]
    last_sync_successful: Optional[bool]
    last_sync_message: Optional[str]
    last_synced: Optional[datetime]
    next_sync: Optional[datetime]
    database_thru_upper: Optional[datetime]
    database_thru_lower: Optional[datetime]


class DataSourcePostBody(HydroLoaderConf):
    name: str
    data_loader: Optional[str]
    data_source_thru: Optional[datetime]
    last_sync_successful: Optional[bool]
    last_sync_message: Optional[str]
    last_synced: Optional[datetime]
    next_sync: Optional[datetime]


@allow_partial
class DataSourcePatchBody(HydroLoaderConf):
    name: str
    data_loader: Optional[str]
    data_source_thru: Optional[datetime]
    last_sync_successful: Optional[bool]
    last_sync_message: Optional[str]
    last_synced: Optional[datetime]
    next_sync: Optional[datetime]