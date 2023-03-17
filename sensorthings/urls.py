from django.urls import path
from django.conf import settings
from django.contrib.auth import authenticate
from ninja.security import HttpBasicAuth
from hydrothings import SensorThingsAPI, SensorThingsComponent
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
    ]
)

urlpatterns = [
    path('v1.1/', st_api_1_1.urls),
    # path('v1.0/', st_api_1_0.urls)
]
