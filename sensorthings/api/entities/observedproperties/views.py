from ninja import Router, Query
from ninja.security import django_auth
from sensorthings.api.core.schemas import Filters


router = Router(tags=['Observed Properties'])


@router.get(
    '/ObservedProperties',
    auth=django_auth
)
def get_observed_properties(request, filters: Filters = Query(...)):
    """"""

    return {}


@router.get(
    '/ObservedProperties({observed_property_id})',
    auth=django_auth
)
def get_observed_property(request, observed_property_id: str):
    """"""

    return {}


@router.post(
    '/ObservedProperties',
    auth=django_auth
)
def create_observed_property(request):
    """"""

    return {}


@router.patch(
    '/ObservedProperties({observed_property_id})',
    auth=django_auth
)
def update_observed_property(request, observed_property_id: str):
    """"""

    return {}


@router.delete(
    '/ObservedProperties({observed_property_id})',
    auth=django_auth
)
def delete_observed_property(request, observed_property_id: str):
    """"""

    return {}
