from django.urls import path
from django.conf import settings
from django.contrib.auth import authenticate
from ninja.security import HttpBasicAuth
from hydrothings import SensorThingsAPI, SensorThingsComponent, SensorThingsEndpoint
from sensorthings import schemas
from sensorthings.engine import SensorThingsEngine


class BasicAuth(HttpBasicAuth):
    def authenticate(self, request, username, password):
        user = authenticate(username=username, password=password)
        if user and user.is_authenticated:
            return user


# st_api_1_0 = SensorThingsAPI(
#     backend='frostserver',
#     title=settings.STAPI_TITLE,
#     version='1.0',
#     description=settings.STAPI_DESCRIPTION
# )

st_api_1_1 = SensorThingsAPI(
    auth=BasicAuth(),
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
            authentication=lambda request: False
        ),
        SensorThingsEndpoint(
            name='update_datastream',
            deprecated=True,
            authentication=lambda request: False
        ),
        SensorThingsEndpoint(
            name='delete_datastream',
            deprecated=True,
            authentication=lambda request: False
        ),
        SensorThingsEndpoint(
            name='create_feature_of_interest',
            deprecated=True,
            authentication=lambda request: False
        ),
        SensorThingsEndpoint(
            name='update_feature_of_interest',
            deprecated=True,
            authentication=lambda request: False
        ),
        SensorThingsEndpoint(
            name='delete_feature_of_interest',
            deprecated=True,
            authentication=lambda request: False
        ),
        SensorThingsEndpoint(
            name='create_historical_location',
            deprecated=True,
            authentication=lambda request: False
        ),
        SensorThingsEndpoint(
            name='update_historical_location',
            deprecated=True,
            authentication=lambda request: False
        ),
        SensorThingsEndpoint(
            name='delete_historical_location',
            deprecated=True,
            authentication=lambda request: False
        ),
        SensorThingsEndpoint(
            name='create_location',
            deprecated=True,
            authentication=lambda request: False
        ),
        SensorThingsEndpoint(
            name='update_location',
            deprecated=True,
            authentication=lambda request: False
        ),
        SensorThingsEndpoint(
            name='delete_location',
            deprecated=True,
            authentication=lambda request: False
        ),
        SensorThingsEndpoint(
            name='create_observation',
            authentication=lambda request: False
        ),
        SensorThingsEndpoint(
            name='update_observation',
            deprecated=True,
            authentication=lambda request: False
        ),
        SensorThingsEndpoint(
            name='delete_observation',
            authentication=lambda request: False
        ),
        SensorThingsEndpoint(
            name='create_observed_property',
            deprecated=True,
            authentication=lambda request: False
        ),
        SensorThingsEndpoint(
            name='update_observed_property',
            deprecated=True,
            authentication=lambda request: False
        ),
        SensorThingsEndpoint(
            name='delete_observed_property',
            deprecated=True,
            authentication=lambda request: False
        ),
        SensorThingsEndpoint(
            name='create_sensor',
            deprecated=True,
            authentication=lambda request: False
        ),
        SensorThingsEndpoint(
            name='update_sensor',
            deprecated=True,
            authentication=lambda request: False
        ),
        SensorThingsEndpoint(
            name='delete_sensor',
            deprecated=True,
            authentication=lambda request: False
        ),
        SensorThingsEndpoint(
            name='create_thing',
            deprecated=True,
            authentication=lambda request: False
        ),
        SensorThingsEndpoint(
            name='update_thing',
            deprecated=True,
            authentication=lambda request: False
        ),
        SensorThingsEndpoint(
            name='delete_thing',
            deprecated=True,
            authentication=lambda request: False
        ),
    ]
)

urlpatterns = [
    path('v1.1/', st_api_1_1.urls),
    # path('v1.0/', st_api_1_0.urls)
]
