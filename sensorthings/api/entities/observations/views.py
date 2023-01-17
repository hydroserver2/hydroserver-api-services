from ninja import Router, Query
from ninja.security import django_auth
from sensorthings.api.core.schemas import Filters


router = Router(tags=['Observations'])


@router.get(
    '/Observations',
    #auth=django_auth
)
def get_observations(request, filters: Filters = Query(...)):
    """"""

    return {}


@router.get(
    '/Observations({observation_id})',
    #auth=django_auth
)
def get_observation(request, observation_id: str):
    """"""

    return {}


@router.post(
    '/Observations',
    #auth=django_auth
)
def create_observation(request):
    """"""

    return {}


@router.patch(
    '/Observations({observation_id})',
    #auth=django_auth
)
def update_observation(request, observation_id: str):
    """"""

    return {}


@router.delete(
    '/Observations({observation_id})',
    #auth=django_auth
)
def delete_observation(request, observation_id: str):
    """"""

    return {}
