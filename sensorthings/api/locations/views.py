from ninja import Router, Query
from ninja.security import django_auth
from sensorthings.api.schemas import Filters


router = Router()


@router.get(
    '/Locations/',
    auth=django_auth,
    tags=['Locations']
)
def get_locations(request, filters: Filters = Query(...)):
    """"""

    return {}


@router.get(
    '/Locations({location_id})/',
    auth=django_auth,
    tags=['Locations']
)
def get_location(request, location_id: str):
    """"""

    return {}


@router.post(
    '/Locations/',
    auth=django_auth,
    tags=['Locations']
)
def create_location(request):
    """"""

    return {}


@router.patch(
    '/Locations({location_id})/',
    auth=django_auth,
    tags=['Locations']
)
def update_location(request, location_id: str):
    """"""

    return {}


@router.delete(
    '/Locations({location_id})/',
    auth=django_auth,
    tags=['Locations']
)
def delete_location(request, location_id: str):
    """"""

    return {}
