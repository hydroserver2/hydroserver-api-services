from ninja import Router, Query
from ninja.security import django_auth
from sensorthings.api.schemas import Filters


router = Router()


@router.get(
    '/Things/',
    auth=django_auth,
    tags=['Things']
)
def get_things(request, filters: Filters = Query(...)):
    """"""

    return {}


@router.get(
    '/Things({thing_id})/',
    auth=django_auth,
    tags=['Things']
)
def get_thing(request, thing_id: str):
    """"""

    return {}


@router.post(
    '/Things/',
    auth=django_auth,
    tags=['Things']
)
def create_thing(request):
    """"""

    return {}


@router.patch(
    '/Things({thing_id})/',
    auth=django_auth,
    tags=['Things']
)
def update_thing(request, thing_id: str):
    """"""

    return {}


@router.delete(
    '/Things({thing_id})/',
    auth=django_auth,
    tags=['Things']
)
def delete_thing(request, thing_id: str):
    """"""

    return {}
