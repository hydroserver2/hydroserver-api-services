from ninja import Router, Query
from ninja.security import django_auth
from sensorthings.api.schemas import Filters


router = Router()


@router.get(
    '/HistoricalLocations/',
    auth=django_auth,
    tags=['Historical Locations']
)
def get_historical_locations(request, filters: Filters = Query(...)):
    """"""

    return {}


@router.get(
    '/HistoricalLocations({historical_location_id})/',
    auth=django_auth,
    tags=['Historical Locations']
)
def get_historical_location(request, historical_location_id: str):
    """"""

    return {}


@router.post(
    '/HistoricalLocations/',
    auth=django_auth,
    tags=['Historical Locations']
)
def create_historical_location(request):
    """"""

    return {}


@router.patch(
    '/HistoricalLocations({historical_location_id})/',
    auth=django_auth,
    tags=['Historical Locations']
)
def update_historical_location(request, historical_location_id: str):
    """"""

    return {}


@router.delete(
    '/HistoricalLocations({historical_location_id})/',
    auth=django_auth,
    tags=['Historical Locations']
)
def delete_historical_location(request, historical_location_id: str):
    """"""

    return {}
