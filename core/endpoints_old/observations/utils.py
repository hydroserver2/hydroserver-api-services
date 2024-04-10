from ninja.errors import HttpError
from django.db.models import Q, Subquery
from django.db.models.query import QuerySet
from uuid import UUID
from typing import List, Optional
from core.models import Observation, ThingAssociation
from accounts.models import Person
from core.endpoints.datastream.utils import check_datastream_by_id


def apply_observation_auth_rules(
        user: Optional[Person],
        observation_query: QuerySet,
        require_ownership: bool = False,
        require_primary_ownership: bool = False,
        require_unaffiliated: bool = False,
        ignore_privacy: bool = False,
        check_result: bool = False
) -> (QuerySet, bool):

    if not user and (require_ownership or require_unaffiliated or require_primary_ownership):
        raise HttpError(403, 'You do not have permission to perform this action on this Datastream.')

    result_exists = observation_query.exists() if check_result is True else None

    auth_query = ThingAssociation.objects.values('thing__datastreams__id')
    auth_filters = Q(~(Q(is_primary_owner=True) & Q(person__is_active=False)))

    if ignore_privacy is False:
        if user:
            auth_filters.add(Q(thing__is_private=False) | (Q(person=user) & Q(owns_thing=True)), Q.AND)
        else:
            auth_filters.add(Q(thing__is_private=False), Q.AND)

    if require_ownership:
        auth_filters.add(Q(person=user), Q.AND)
        auth_filters.add(Q(owns_thing=True), Q.AND)

    if require_primary_ownership:
        auth_filters.add(Q(person=user) & Q(is_primary_owner=True), Q.AND)

    if require_unaffiliated:
        auth_filters.add(Q(person=user) & Q(owns_thing=False), Q.AND)

    if require_ownership or require_primary_ownership:
        auth_query = auth_query.filter(auth_filters).distinct()
        observation_query = observation_query.filter(datastream_id__in=Subquery(auth_query))
    else:
        auth_query = auth_query.exclude(auth_filters).distinct()
        observation_query = observation_query.filter(~Q(datastream_id__in=Subquery(auth_query)))

    return observation_query, result_exists


def query_observations(
        user: Optional[Person],
        check_result_exists: bool = False,
        require_ownership: bool = False,
        require_primary_ownership: bool = False,
        require_unaffiliated: bool = False,
        ignore_privacy: bool = False,
        observation_ids: Optional[List[UUID]] = None,
        datastream_ids: Optional[List[UUID]] = None,
        feature_of_interest_ids: Optional[List[UUID]] = None,
) -> (QuerySet, bool):

    observation_query = Observation.objects

    if observation_ids:
        observation_query = observation_query.filter(id__in=observation_ids)

    if datastream_ids:
        observation_query = observation_query.filter(datastream_id__in=datastream_ids)

    if feature_of_interest_ids:
        observation_query = observation_query.filter(feature_of_interest_id__in=feature_of_interest_ids)

    # observation_query = observation_query.select_related(
    #     'datastream', 'feature_of_interest'
    # )

    observation_query, result_exists = apply_observation_auth_rules(
        user=user,
        observation_query=observation_query,
        require_ownership=require_ownership,
        require_primary_ownership=require_primary_ownership,
        require_unaffiliated=require_unaffiliated,
        ignore_privacy=ignore_privacy,
        check_result=check_result_exists
    )

    return observation_query, result_exists


def check_observation_by_id(
        user: Optional[Person],
        observation_id: UUID,
        require_ownership: bool = False,
        require_primary_ownership: bool = False,
        require_unaffiliated: bool = False,
        ignore_privacy: bool = False,
        raise_http_errors: bool = False
) -> bool:

    observation_query, observation_exists = query_observations(
        user=user,
        datastream_ids=[observation_id],
        require_ownership=require_ownership,
        require_primary_ownership=require_primary_ownership,
        require_unaffiliated=require_unaffiliated,
        ignore_privacy=ignore_privacy,
        check_result_exists=True
    )

    observation = observation_query.exists()

    if raise_http_errors and not observation_exists:
        raise HttpError(404, 'Observation not found.')
    if raise_http_errors and observation_exists and not observation:
        raise HttpError(403, 'You do not have permission to perform this action on this Observation.')

    return observation


def get_observation_by_id(
        user: Optional[Person],
        observation_id: UUID,
        require_ownership: bool = False,
        require_primary_ownership: bool = False,
        require_unaffiliated: bool = False,
        ignore_privacy: bool = False,
        raise_http_errors: bool = True
):

    observation_query, observation_exists = query_observations(
        user=user,
        observation_ids=[observation_id],
        require_ownership=require_ownership,
        require_primary_ownership=require_primary_ownership,
        require_unaffiliated=require_unaffiliated,
        ignore_privacy=ignore_privacy,
        check_result_exists=True
    )

    observation = next(iter(observation_query.all()), None)

    if raise_http_errors and not observation_exists:
        raise HttpError(404, 'Observation not found.')
    if raise_http_errors and observation_exists and not observation:
        raise HttpError(403, 'You do not have permission to perform this action on this Observation.')

    return observation


def build_observation_response(observation):

    return {
        'id': observation.id,
        **{field: getattr(observation, field) for field in ObservationFields.__fields__.keys()},
    }


def check_related_fields(user, data):

    if data.datastream_id:
        check_datastream_by_id(
            user=user,
            datastream_id=data.datastream_id,
            require_ownership=True,
            raise_http_errors=True
        )

    if data.feature_of_interest_id:
        raise HttpError(404, 'Feature of interest not found.')
