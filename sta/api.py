from django.db import transaction
from sensorthings import SensorThingsExtension
from sensorthings.factories import SensorThingsEndpointHookFactory
from sta.schemas import sensorthings as schemas
from hydroserver.security import session_auth, bearer_auth, apikey_auth, anonymous_auth


hydroserver_extension = SensorThingsExtension(
    endpoint_hooks=[
        SensorThingsEndpointHookFactory(
            endpoint_name="list_datastreams",
            view_authentication=[
                session_auth,
                bearer_auth,
                apikey_auth,
                anonymous_auth,
            ],
            view_response_schema=schemas.DatastreamListResponse,
        ),
        SensorThingsEndpointHookFactory(
            endpoint_name="get_datastream",
            view_authentication=[
                session_auth,
                bearer_auth,
                apikey_auth,
                anonymous_auth,
            ],
            view_response_schema=schemas.DatastreamGetResponse,
        ),
        SensorThingsEndpointHookFactory(
            endpoint_name="create_datastream",
            enabled=False,
            view_authentication=lambda request: False,
        ),
        SensorThingsEndpointHookFactory(
            endpoint_name="update_datastream",
            enabled=False,
            view_authentication=lambda request: False,
        ),
        SensorThingsEndpointHookFactory(
            endpoint_name="delete_datastream",
            enabled=False,
            view_authentication=lambda request: False,
        ),
        SensorThingsEndpointHookFactory(
            endpoint_name="list_features_of_interest",
            view_authentication=[
                session_auth,
                bearer_auth,
                apikey_auth,
                anonymous_auth,
            ],
        ),
        SensorThingsEndpointHookFactory(
            endpoint_name="get_feature_of_interest",
            view_authentication=[
                session_auth,
                bearer_auth,
                apikey_auth,
                anonymous_auth,
            ],
        ),
        SensorThingsEndpointHookFactory(
            endpoint_name="create_feature_of_interest",
            enabled=False,
            view_authentication=lambda request: False,
        ),
        SensorThingsEndpointHookFactory(
            endpoint_name="update_feature_of_interest",
            enabled=False,
            view_authentication=lambda request: False,
        ),
        SensorThingsEndpointHookFactory(
            endpoint_name="delete_feature_of_interest",
            enabled=False,
            view_authentication=lambda request: False,
        ),
        SensorThingsEndpointHookFactory(
            endpoint_name="list_historical_locations",
            view_authentication=[
                session_auth,
                bearer_auth,
                apikey_auth,
                anonymous_auth,
            ],
        ),
        SensorThingsEndpointHookFactory(
            endpoint_name="get_historical_location",
            view_authentication=[
                session_auth,
                bearer_auth,
                apikey_auth,
                anonymous_auth,
            ],
        ),
        SensorThingsEndpointHookFactory(
            endpoint_name="create_historical_location",
            enabled=False,
            view_authentication=lambda request: False,
        ),
        SensorThingsEndpointHookFactory(
            endpoint_name="update_historical_location",
            enabled=False,
            view_authentication=lambda request: False,
        ),
        SensorThingsEndpointHookFactory(
            endpoint_name="delete_historical_location",
            enabled=False,
            view_authentication=lambda request: False,
        ),
        SensorThingsEndpointHookFactory(
            endpoint_name="list_locations",
            view_authentication=[
                session_auth,
                bearer_auth,
                apikey_auth,
                anonymous_auth,
            ],
            view_response_schema=schemas.LocationListResponse,
        ),
        SensorThingsEndpointHookFactory(
            endpoint_name="get_location",
            view_authentication=[
                session_auth,
                bearer_auth,
                apikey_auth,
                anonymous_auth,
            ],
            view_response_schema=schemas.LocationGetResponse,
        ),
        SensorThingsEndpointHookFactory(
            endpoint_name="create_location",
            enabled=False,
            view_authentication=lambda request: False,
        ),
        SensorThingsEndpointHookFactory(
            endpoint_name="update_location",
            enabled=False,
            view_authentication=lambda request: False,
        ),
        SensorThingsEndpointHookFactory(
            endpoint_name="delete_location",
            enabled=False,
            view_authentication=lambda request: False,
        ),
        SensorThingsEndpointHookFactory(
            endpoint_name="list_observations",
            view_authentication=[
                session_auth,
                bearer_auth,
                apikey_auth,
                anonymous_auth,
            ],
            view_response_schema=schemas.ObservationListResponse,
        ),
        SensorThingsEndpointHookFactory(
            endpoint_name="get_observation",
            view_authentication=[
                session_auth,
                bearer_auth,
                apikey_auth,
                anonymous_auth,
            ],
            view_response_schema=schemas.ObservationGetResponse,
        ),
        SensorThingsEndpointHookFactory(
            endpoint_name="create_observation",
            view_wrapper=transaction.atomic,
            view_authentication=[
                session_auth,
                bearer_auth,
                apikey_auth,
                anonymous_auth,
            ],
            view_body_schema=schemas.ObservationPostBody,
        ),
        SensorThingsEndpointHookFactory(
            endpoint_name="create_observations",
            view_wrapper=transaction.atomic,
            view_authentication=[
                session_auth,
                bearer_auth,
                apikey_auth,
                anonymous_auth,
            ],
            view_body_schema=schemas.ObservationDataArrayPostBody,
        ),
        SensorThingsEndpointHookFactory(
            endpoint_name="update_observation",
            enabled=False,
            view_authentication=lambda request: False,
        ),
        SensorThingsEndpointHookFactory(
            endpoint_name="delete_observation",
            enabled=False,
            view_authentication=lambda request: False,
        ),
        SensorThingsEndpointHookFactory(
            endpoint_name="list_observed_properties",
            view_authentication=[
                session_auth,
                bearer_auth,
                apikey_auth,
                anonymous_auth,
            ],
            view_response_schema=schemas.ObservedPropertyListResponse,
        ),
        SensorThingsEndpointHookFactory(
            endpoint_name="get_observed_property",
            view_authentication=[
                session_auth,
                bearer_auth,
                apikey_auth,
                anonymous_auth,
            ],
            view_response_schema=schemas.ObservedPropertyGetResponse,
        ),
        SensorThingsEndpointHookFactory(
            endpoint_name="create_observed_property",
            enabled=False,
            view_authentication=lambda request: False,
        ),
        SensorThingsEndpointHookFactory(
            endpoint_name="update_observed_property",
            enabled=False,
            view_authentication=lambda request: False,
        ),
        SensorThingsEndpointHookFactory(
            endpoint_name="delete_observed_property",
            enabled=False,
            view_authentication=lambda request: False,
        ),
        SensorThingsEndpointHookFactory(
            endpoint_name="list_sensors",
            view_authentication=[
                session_auth,
                bearer_auth,
                apikey_auth,
                anonymous_auth,
            ],
            view_response_schema=schemas.SensorListResponse,
        ),
        SensorThingsEndpointHookFactory(
            endpoint_name="get_sensor",
            view_authentication=[
                session_auth,
                bearer_auth,
                apikey_auth,
                anonymous_auth,
            ],
            view_response_schema=schemas.SensorGetResponse,
        ),
        SensorThingsEndpointHookFactory(
            endpoint_name="create_sensor",
            enabled=False,
            view_authentication=lambda request: False,
        ),
        SensorThingsEndpointHookFactory(
            endpoint_name="update_sensor",
            enabled=False,
            view_authentication=lambda request: False,
        ),
        SensorThingsEndpointHookFactory(
            endpoint_name="delete_sensor",
            enabled=False,
            view_authentication=lambda request: False,
        ),
        SensorThingsEndpointHookFactory(
            endpoint_name="list_things",
            view_authentication=[
                session_auth,
                bearer_auth,
                apikey_auth,
                anonymous_auth,
            ],
            view_response_schema=schemas.ThingListResponse,
        ),
        SensorThingsEndpointHookFactory(
            endpoint_name="get_thing",
            view_authentication=[
                session_auth,
                bearer_auth,
                apikey_auth,
                anonymous_auth,
            ],
            view_response_schema=schemas.ThingGetResponse,
        ),
        SensorThingsEndpointHookFactory(
            endpoint_name="create_thing",
            enabled=False,
            view_authentication=lambda request: False,
        ),
        SensorThingsEndpointHookFactory(
            endpoint_name="update_thing",
            enabled=False,
            view_authentication=lambda request: False,
        ),
        SensorThingsEndpointHookFactory(
            endpoint_name="delete_thing",
            enabled=False,
            view_authentication=lambda request: False,
        ),
    ],
)
