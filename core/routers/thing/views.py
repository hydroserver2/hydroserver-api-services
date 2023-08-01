from ninja import Router, Query
from django.http import HttpRequest, HttpResponse
from django.db import transaction
from django.db.models import Q
from typing import List
from core.routers.thing.schemas import *
from sites.models import Thing, ThingAssociation


router = Router(tags=['Things'])


def get_thing_ownership(thing, thing_associations, authenticated_user):


    return {
        'is_primary_owner': False,
        'owners': thing_associations
    }


@router.get(
    '/things',
    response={
        200: List[ThingGetResponse]
    }
)
def get_things(
        request: HttpRequest,
        # params: ThingQueryParams = Query(...)
):
    """"""

    if getattr(request, 'authenticated_user', None):
        owned_things = ThingAssociation.objects.filter(
            person=request.authenticated_user
        ).values_list('thing', flat=True)
    else:
        owned_things = []

    things = Thing.objects.filter(Q(is_private=False) | Q(id__in=owned_things)).values(
        'id', 'name', 'description', 'sampling_feature_type', 'sampling_feature_code', 'site_type', 'is_private',
        'location__latitude', 'location__longitude', 'location__elevation', 'location__state', 'location__county',
        'location__city'
    )

    thing_associations = ThingAssociation.objects.filter(thing__id__in=[thing['id'] for thing in things]).values(
        'thing_id', 'person__first_name', 'person__last_name', 'person__organization', 'person__email',
        'is_primary_owner', 'owns_thing', 'follows_thing'
    )

    thing_associations_dict = {}
    for thing_association in thing_associations:
        thing_associations_dict.setdefault(thing_association['thing_id'], []).append(thing_association)

    things = [
        {
            **get_thing_ownership(
                thing,
                thing_associations_dict.get(thing['id'], []),
                getattr(request, 'authenticated_user', None)
            ),
            **thing
        } for thing in things
    ]

    return things



