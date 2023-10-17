import operator
from ninja.errors import HttpError
from django.db.models import Q, Count, Prefetch
from django.db.models.query import QuerySet
from uuid import UUID
from typing import List, Optional
from functools import reduce
from core.models import Person, Thing, ThingAssociation
from .schemas import AssociationFields, PersonFields, OrganizationFields, ThingFields, LocationFields


def apply_thing_auth_rules(
        user: Optional[Person],
        thing_query: QuerySet,
        require_ownership: bool = False,
        require_primary_ownership: bool = False,
        require_unaffiliated: bool = False,
        ignore_privacy: bool = False,
        check_result: bool = False
) -> (QuerySet, bool):

    if not user and (require_ownership or require_unaffiliated or require_primary_ownership):
        raise HttpError(403, 'You are not authorized to access this Thing.')

    result_exists = thing_query.exists() if check_result is True else None

    auth_filters = []

    if ignore_privacy is False:
        if user:
            auth_filters.append((
                Q(is_private=False) | (Q(associates__person=user) & Q(associates__owns_thing=True))
            ))
        else:
            auth_filters.append(Q(is_private=False))

    if require_ownership:
        auth_filters.append(Q(associates__person=user) & Q(associates__owns_thing=True))

    if require_primary_ownership:
        auth_filters.append(Q(associates__person=user) & Q(associates__is_primary_owner=True))

    if require_unaffiliated:
        auth_filters.append(Q(associates__person=user) & Q(associates__owns_thing=False))

    thing_query = thing_query.annotate(
        associates_count=Count(
            'associates', filter=reduce(operator.and_, auth_filters) if auth_filters else None
        )
    ).filter(
        associates_count__gt=0
    )

    return thing_query, result_exists


def query_things(
        user: Optional[Person],
        check_result_exists: bool = False,
        require_ownership: bool = False,
        require_primary_ownership: bool = False,
        require_unaffiliated: bool = False,
        ignore_privacy: bool = False,
        thing_ids: Optional[List[UUID]] = None,
        prefetch_photos: bool = False,
        prefetch_datastreams: bool = False
) -> (QuerySet, bool):

    thing_query = Thing.objects

    if thing_ids:
        thing_query = thing_query.filter(id__in=thing_ids)

    associates_prefetch = Prefetch(
        'associates', queryset=ThingAssociation.objects.select_related('person', 'person__organization')
    )

    thing_query = thing_query.select_related('location').prefetch_related(associates_prefetch)

    if prefetch_photos:
        thing_query = thing_query.prefetch_related('photos')

    if prefetch_datastreams:
        thing_query = thing_query.prefetch_related('datastreams')

    thing_query, result_exists = apply_thing_auth_rules(
        user=user,
        thing_query=thing_query,
        require_ownership=require_ownership,
        require_primary_ownership=require_primary_ownership,
        require_unaffiliated=require_unaffiliated,
        ignore_privacy=ignore_privacy,
        check_result=check_result_exists
    )

    return thing_query, result_exists


def check_thing_by_id(
        user: Optional[Person],
        thing_id: UUID,
        require_ownership: bool = False,
        require_primary_ownership: bool = False,
        require_unaffiliated: bool = False,
        ignore_privacy: bool = False,
        raise_http_errors: bool = False
) -> bool:

    thing_query, thing_exists = query_things(
        user=user,
        thing_ids=[thing_id],
        require_ownership=require_ownership,
        require_primary_ownership=require_primary_ownership,
        require_unaffiliated=require_unaffiliated,
        ignore_privacy=ignore_privacy,
        check_result_exists=True
    )

    thing = thing_query.exists()

    if raise_http_errors and not thing_exists:
        raise HttpError(404, 'Thing not found.')
    if raise_http_errors and thing_exists and not thing:
        raise HttpError(403, 'You do not have permission to perform this action on this Thing.')

    return thing


def get_thing_by_id(
        user: Optional[Person],
        thing_id: UUID,
        require_ownership: bool = False,
        require_primary_ownership: bool = False,
        require_unaffiliated: bool = False,
        ignore_privacy: bool = False,
        prefetch_photos: bool = False,
        prefetch_datastreams: bool = False,
        raise_http_errors: bool = True
):

    thing_query, thing_exists = query_things(
        user=user,
        thing_ids=[thing_id],
        require_ownership=require_ownership,
        require_primary_ownership=require_primary_ownership,
        require_unaffiliated=require_unaffiliated,
        ignore_privacy=ignore_privacy,
        prefetch_photos=prefetch_photos,
        prefetch_datastreams=prefetch_datastreams,
        check_result_exists=True
    )

    thing = next(iter(thing_query.all()), None)

    if raise_http_errors and not thing_exists:
        raise HttpError(404, 'Thing not found.')
    if raise_http_errors and thing_exists and not thing:
        raise HttpError(403, 'You do not have permission to perform this action on this Thing.')

    return thing


def build_thing_response(user, thing):

    thing_association = next(iter([
        associate for associate in thing.associates.all() if user and associate.person.id == user.id
    ]), None)

    return {
        'id': thing.id,
        'is_private': thing.is_private,
        'is_primary_owner': getattr(thing_association, 'is_primary_owner', False),
        'owns_thing': getattr(thing_association, 'owns_thing', False),
        'follows_thing': getattr(thing_association, 'follows_thing', False),
        'owners': [{
            **{field: getattr(associate, field) for field in AssociationFields.__fields__.keys()},
            **{field: getattr(associate.person, field) for field in PersonFields.__fields__.keys()},
            **{field: getattr(associate.person.organization, field, None)
               for field in OrganizationFields.__fields__.keys()},
        } for associate in thing.associates.all() if associate.owns_thing is True],
        **{field: getattr(thing, field) for field in ThingFields.__fields__.keys()},
        **{field: getattr(thing.location, field) for field in LocationFields.__fields__.keys()}
    }
