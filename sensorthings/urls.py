from django.urls import path
from django.conf import settings
from hydrothings import SensorThingsAPI, SensorThingsComponent, SensorThingsEndpoint
from sensorthings import schemas
from sensorthings.engine import SensorThingsEngine
from sensorthings.auth import observation_authorization, BasicAuth


st_api_1_1 = SensorThingsAPI(
    engine=SensorThingsEngine,
    title=settings.STAPI_TITLE,
    version='1.1',
    description=settings.STAPI_DESCRIPTION,
    components=[
        SensorThingsComponent(
            name='datastream',
            component_schema=schemas.Datastream
        ),
        SensorThingsComponent(
            name='location',
            component_schema=schemas.Location
        ),
        SensorThingsComponent(
            name='observed_property',
            component_schema=schemas.ObservedProperty
        ),
        SensorThingsComponent(
            name='sensor',
            component_schema=schemas.Sensor
        ),
        SensorThingsComponent(
            name='thing',
            component_schema=schemas.Thing
        )
    ],
    endpoints=[
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
            name='create_observation',
            authentication=BasicAuth(),
            authorization=observation_authorization
        ),
        SensorThingsEndpoint(
            name='update_observation',
            deprecated=True,
            authorization=lambda request, observation_id, observation: False
        ),
        SensorThingsEndpoint(
            name='delete_observation',
            authentication=BasicAuth(),
            authorization=observation_authorization
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
