from ninja import Router, Query
from ninja.security import django_auth
from sensorthings.api.schemas import Filters


router = Router()


@router.get(
    '/ObservedProperties/',
    auth=django_auth,
    tags=['Observed Properties']
)
def get_observed_properties(request, filters: Filters = Query(...)):
    """"""

    return {}


@router.get(
    '/ObservedProperties({observed_property_id})/',
    auth=django_auth,
    tags=['Observed Properties']
)
def get_observed_property(request, observed_property_id: str):
    """"""

    return {}


@router.post(
    '/ObservedProperties/',
    auth=django_auth,
    tags=['Observed Properties']
)
def create_observed_property(request):
    """"""

    return {}


@router.patch(
    '/ObservedProperties({observed_property_id})/',
    auth=django_auth,
    tags=['Observed Properties']
)
def update_observed_property(request, observed_property_id: str):
    """"""

    return {}


@router.delete(
    '/ObservedProperties({observed_property_id})/',
    auth=django_auth,
    tags=['Observed Properties']
)
def delete_observed_property(request, observed_property_id: str):
    """"""

    return {}
