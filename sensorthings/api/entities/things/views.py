from ninja import Router, Query
from ninja.security import django_auth
from django.http import HttpRequest, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.urls.exceptions import Http404
from sensorthings.api.core.schemas import Filters
from sensorthings.models import Thing
from .schemas import ThingPostBody, ThingPatchBody, ThingListResponse, ThingGetResponse


router = Router(tags=['Things'])


@router.get(
    '/Things',
    auth=django_auth,
    response=ThingListResponse,
    by_alias=True,
    url_name='list_thing'
)
def get_things(request: HttpRequest, filters: Filters = Query(...)):
    """"""

    return {}


@router.get(
    '/Things({thing_id})',
    auth=django_auth,
    response=ThingGetResponse,
    by_alias=True
)
def get_thing(request: HttpRequest, thing_id: str):
    """"""

    return {}


@router.post(
    '/Things',
    auth=django_auth,
    response={201: None}
)
def create_thing(request: HttpRequest, response: HttpResponse, thing: ThingPostBody):
    """"""

    thing = Thing(**thing.dict())
    thing.save()

    response['location'] = thing.get_ref(request)

    return 201, None


@router.patch(
    '/Things({thing_id})',
    auth=django_auth,
    response={204: None}
)
def update_thing(request: HttpRequest, thing_id: str, thing: ThingPatchBody):
    """"""

    try:
        db_thing = Thing.objects.get(pk=thing_id)
    except ObjectDoesNotExist:
        raise Http404

    for attr, value in thing.dict(exclude_unset=True).items():
        setattr(db_thing, attr, value)

    db_thing.save()

    return 204, None


@router.delete(
    '/Things({thing_id})',
    auth=django_auth
)
def delete_thing(request: HttpRequest, thing_id: str):
    """"""

    return {}
