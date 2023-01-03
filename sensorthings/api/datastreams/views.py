from ninja import Router, Query
from ninja.security import django_auth
from sensorthings.api.schemas import Filters


router = Router()


@router.get(
    '/DataStreams/',
    auth=django_auth,
    tags=['Data Streams']
)
def get_data_streams(request, filters: Filters = Query(...)):
    """"""

    return {}


@router.get(
    '/DataStreams({data_stream_id})/',
    auth=django_auth,
    tags=['Data Streams']
)
def get_data_stream(request, data_stream_id: str):
    """"""

    return {}


@router.post(
    '/DataStreams/',
    auth=django_auth,
    tags=['Data Streams']
)
def create_data_stream(request):
    """"""

    return {}


@router.patch(
    '/DataStreams({data_stream_id})/',
    auth=django_auth,
    tags=['Data Streams']
)
def update_data_stream(request, data_stream_id: str):
    """"""

    return {}


@router.delete(
    '/DataStreams({data_stream_id})/',
    auth=django_auth,
    tags=['Data Streams']
)
def delete_data_stream(request, data_stream_id: str):
    """"""

    return {}
