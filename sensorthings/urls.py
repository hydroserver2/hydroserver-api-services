from django.urls import path
from django.conf import settings
from hydrothings import SensorThingsAPI, SensorThingsEndpoint
from sensorthings.schemas import ThingGetResponse


st_api_1_0 = SensorThingsAPI(
    backend='sensorthings',
    title=settings.STAPI_TITLE,
    version='1.0',
    description=settings.STAPI_DESCRIPTION
)

st_api_1_1 = SensorThingsAPI(
    backend='sensorthings',
    title=settings.STAPI_TITLE,
    version='1.1',
    description=settings.STAPI_DESCRIPTION,
    endpoints=[
        SensorThingsEndpoint(
            name='list_thing',
        ),
        SensorThingsEndpoint(
            name='get_thing',
            response_schema=ThingGetResponse
        )
    ]
)

urlpatterns = [
    path('v1.1/', st_api_1_1.urls),
    path('v1.0/', st_api_1_0.urls)
]
