from ninja import Router, Query
from ninja.security import django_auth
from sensorthings.api.schemas import Filters


router = Router(tags=['Sensors'])


@router.get(
    '/Sensors',
    auth=django_auth
)
def get_sensors(request, filters: Filters = Query(...)):
    """"""

    return {}


@router.get(
    '/Sensors({sensor_id})',
    auth=django_auth
)
def get_sensor(request, sensor_id: str):
    """"""

    return {}


@router.post(
    '/Sensors',
    auth=django_auth
)
def create_sensor(request):
    """"""

    return {}


@router.patch(
    '/Sensors({sensor_id})',
    auth=django_auth
)
def update_sensor(request, sensor_id: str):
    """"""

    return {}


@router.delete(
    '/Sensors({sensor_id})',
    auth=django_auth
)
def delete_sensor(request, sensor_id: str):
    """"""

    return {}
