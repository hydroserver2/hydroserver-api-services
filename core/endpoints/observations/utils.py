import operator
from ninja.errors import HttpError
from django.db.models import Q, Count
from django.db.models.query import QuerySet
from uuid import UUID
from typing import List, Optional
from functools import reduce
from core.models import Person, Observation
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

    auth_filters = []

    if ignore_privacy is False:
        if user:
            auth_filters.append((
                Q(datastream__thing__is_private=False) |
                (Q(datastream__thing__associates__person=user) & Q(datastream__thing__associates__owns_thing=True))
            ))
        else:
            auth_filters.append(Q(datastream__thing__is_private=False))

    if require_ownership:
        auth_filters.append(
            Q(datastream__thing__associates__person=user) &
            Q(datastream__thing__associates__owns_thing=True)
    )

    if require_primary_ownership:
        auth_filters.append(
            Q(datastream__thing__associates__person=user) &
            Q(datastream__thing__associates__is_primary_owner=True)
        )

    if require_unaffiliated:
        auth_filters.append(
            Q(datastream__thing__associates__person=user) &
            Q(datastream__thing__associates__owns_thing=False)
        )

    observation_query = observation_query.annotate(
        associates_count=Count(
            'datastream__thing__associates', filter=reduce(operator.and_, auth_filters) if auth_filters else None
        )
    ).filter(
        associates_count__gt=0
    )

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

    observation_query = observation_query.select_related(
        'datastream', 'feature_of_interest'
    )

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
