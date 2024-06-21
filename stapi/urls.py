from django.urls import path
from sensorthings import SensorThingsAPI, SensorThingsEndpoint
from stapi import schemas
from stapi.engine import HydroServerSensorThingsEngine
from hydroserver.auth import JWTAuth, BasicAuth, anonymous_auth


st_api_1_1 = SensorThingsAPI(
    engine=HydroServerSensorThingsEngine,
    title='HydroServer SensorThings API',
    version='1.1',
    description='This is the documentation for the HydroServer SensorThings API implementation.',
    endpoints=[
        SensorThingsEndpoint(
            name='list_datastream',
            authentication=[JWTAuth(), BasicAuth(), anonymous_auth],
            response_schema=schemas.DatastreamListResponse
        ),
        SensorThingsEndpoint(
            name='get_datastream',
            authentication=[JWTAuth(), BasicAuth(), anonymous_auth],
            response_schema=schemas.DatastreamGetResponse
        ),
        SensorThingsEndpoint(
            name='create_datastream',
            deprecated=True,
            authorization=lambda request, datastream: False
        ),
        SensorThingsEndpoint(
            name='update_datastream',
            deprecated=True,
            authorization=lambda request, datastream_id, datastream: False
        ),
        SensorThingsEndpoint(
            name='delete_datastream',
            deprecated=True,
            authorization=lambda request, datastream_id: False
        ),
        SensorThingsEndpoint(
            name='list_feature_of_interest',
            authentication=[JWTAuth(), BasicAuth(), anonymous_auth]
        ),
        SensorThingsEndpoint(
            name='get_feature_of_interest',
            authentication=[JWTAuth(), BasicAuth(), anonymous_auth]
        ),
        SensorThingsEndpoint(
            name='create_feature_of_interest',
            deprecated=True,
            authorization=lambda request, feature_of_interest: False
        ),
        SensorThingsEndpoint(
            name='update_feature_of_interest',
            deprecated=True,
            authorization=lambda request, feature_of_interest_id, feature_of_interest: False
        ),
        SensorThingsEndpoint(
            name='delete_feature_of_interest',
            deprecated=True,
            authorization=lambda request, feature_of_interest_id: False
        ),
        SensorThingsEndpoint(
            name='list_historical_location',
            authentication=[JWTAuth(), BasicAuth(), anonymous_auth]
        ),
        SensorThingsEndpoint(
            name='get_historical_location',
            authentication=[JWTAuth(), BasicAuth(), anonymous_auth]
        ),
        SensorThingsEndpoint(
            name='create_historical_location',
            deprecated=True,
            authorization=lambda request, historical_location: False
        ),
        SensorThingsEndpoint(
            name='update_historical_location',
            deprecated=True,
            authorization=lambda request, historical_location_id, historical_location: False
        ),
        SensorThingsEndpoint(
            name='delete_historical_location',
            deprecated=True,
            authorization=lambda request, historical_location_id: False
        ),
        SensorThingsEndpoint(
            name='list_location',
            authentication=[JWTAuth(), BasicAuth(), anonymous_auth],
            response_schema=schemas.LocationListResponse
        ),
        SensorThingsEndpoint(
            name='get_location',
            authentication=[JWTAuth(), BasicAuth(), anonymous_auth],
            response_schema=schemas.LocationGetResponse
        ),
        SensorThingsEndpoint(
            name='create_location',
            deprecated=True,
            authorization=lambda request, location: False
        ),
        SensorThingsEndpoint(
            name='update_location',
            deprecated=True,
            authorization=lambda request, location_id, location: False
        ),
        SensorThingsEndpoint(
            name='delete_location',
            deprecated=True,
            authorization=lambda request, location_id: False
        ),
        SensorThingsEndpoint(
            name='list_observation',
            authentication=[JWTAuth(), BasicAuth(), anonymous_auth],
            response_schema=[schemas.ObservationListResponse]
        ),
        SensorThingsEndpoint(
            name='get_observation',
            authentication=[JWTAuth(), BasicAuth(), anonymous_auth],
            response_schema=schemas.ObservationGetResponse
        ),
        SensorThingsEndpoint(
            name='create_observation',
            authentication=[JWTAuth(), BasicAuth()],
            body_schema=schemas.ObservationPostBody
        ),
        SensorThingsEndpoint(
            name='create_observations',
            authentication=[JWTAuth(), BasicAuth()],
            body_schema=schemas.ObservationPatchBody
        ),
        SensorThingsEndpoint(
            name='update_observation',
            deprecated=True,
            authorization=lambda request, observation_id, observation: False,
            body_schema=schemas.ObservationPatchBody
        ),
        SensorThingsEndpoint(
            name='delete_observation',
            deprecated=True,
            authorization=lambda request, observation_id: False,
        ),
        SensorThingsEndpoint(
            name='list_observed_property',
            authentication=[JWTAuth(), BasicAuth(), anonymous_auth],
            response_schema=schemas.ObservedPropertyListResponse
        ),
        SensorThingsEndpoint(
            name='get_observed_property',
            authentication=[JWTAuth(), BasicAuth(), anonymous_auth],
            response_schema=schemas.ObservedPropertyGetResponse
        ),
        SensorThingsEndpoint(
            name='create_observed_property',
            deprecated=True,
            authorization=lambda request, observed_property: False
        ),
        SensorThingsEndpoint(
            name='update_observed_property',
            deprecated=True,
            authorization=lambda request, observed_property_id, observed_property: False
        ),
        SensorThingsEndpoint(
            name='delete_observed_property',
            deprecated=True,
            authorization=lambda request, observed_property_id: False
        ),
        SensorThingsEndpoint(
            name='list_sensor',
            authentication=[JWTAuth(), BasicAuth(), anonymous_auth],
            response_schema=schemas.SensorListResponse
        ),
        SensorThingsEndpoint(
            name='get_sensor',
            authentication=[JWTAuth(), BasicAuth(), anonymous_auth],
            response_schema=schemas.SensorGetResponse
        ),
        SensorThingsEndpoint(
            name='create_sensor',
            deprecated=True,
            authorization=lambda request, sensor: False
        ),
        SensorThingsEndpoint(
            name='update_sensor',
            deprecated=True,
            authorization=lambda request, sensor_id, sensor: False
        ),
        SensorThingsEndpoint(
            name='delete_sensor',
            deprecated=True,
            authorization=lambda request, sensor_id: False
        ),
        SensorThingsEndpoint(
            name='list_thing',
            authentication=[JWTAuth(), BasicAuth(), anonymous_auth],
            response_schema=schemas.ThingListResponse
        ),
        SensorThingsEndpoint(
            name='get_thing',
            authentication=[JWTAuth(), BasicAuth(), anonymous_auth],
            response_schema=schemas.ThingGetResponse
        ),
        SensorThingsEndpoint(
            name='create_thing',
            deprecated=True,
            authorization=lambda request, thing: False
        ),
        SensorThingsEndpoint(
            name='update_thing',
            deprecated=True,
            authorization=lambda request, thing_id, thing: False
        ),
        SensorThingsEndpoint(
            name='delete_thing',
            deprecated=True,
            authorization=lambda request, thing_id: False
        ),
    ]
)

urlpatterns = [
    path('v1.1/', st_api_1_1.urls),
]
