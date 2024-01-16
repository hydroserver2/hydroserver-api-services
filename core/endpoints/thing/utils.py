import operator
from datetime import datetime
from ninja.errors import HttpError
from django.db.models import Q, Count, Prefetch
from django.db.models.query import QuerySet
from uuid import UUID
from typing import List, Optional
from functools import reduce
from hsmodels.schemas.fields import PointCoverage
from core.models import Person, Thing, ThingAssociation
from .schemas import AssociationFields, PersonFields, OrganizationFields, ThingFields, LocationFields


def apply_thing_auth_rules(
        user: Optional[Person],
        thing_query: QuerySet,
        require_ownership: bool = False,
        require_primary_ownership: bool = False,
        require_unaffiliated: bool = False,
        ignore_privacy: bool = False,
        check_result: bool = False,
        raise_http_errors: bool = True
) -> (QuerySet, bool):

    result_exists = thing_query.exists() if check_result is True else None

    if not user and (require_ownership or require_unaffiliated or require_primary_ownership):
        if raise_http_errors is True:
            raise HttpError(403, 'You do not have permission to perform this action on this Thing.')
        else:
            return thing_query.none(), result_exists

    auth_filters = [
        ~(Q(associates__is_primary_owner=True) & Q(associates__person__is_active=False))
    ]

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


def apply_recent_thing_filter(
        thing_query: QuerySet,
        modified_since: datetime
) -> QuerySet:

    thing_query = thing_query.filter(
       log__history_date__gt=modified_since
    )

    return thing_query


def query_things(
        user: Optional[Person],
        check_result_exists: bool = False,
        require_ownership: bool = False,
        require_primary_ownership: bool = False,
        require_unaffiliated: bool = False,
        ignore_privacy: bool = False,
        thing_ids: Optional[List[UUID]] = None,
        prefetch_photos: bool = False,
        prefetch_datastreams: bool = False,
        prefetch_tags: bool = False,
        modified_since: Optional[datetime] = None,
        raise_http_errors: Optional[bool] = True
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

    if prefetch_tags:
        thing_query = thing_query.prefetch_related('tags')

    if modified_since:
        thing_query = thing_query.prefetch_related('log')
        thing_query = apply_recent_thing_filter(thing_query, modified_since)

    thing_query, result_exists = apply_thing_auth_rules(
        user=user,
        thing_query=thing_query,
        require_ownership=require_ownership,
        require_primary_ownership=require_primary_ownership,
        require_unaffiliated=require_unaffiliated,
        ignore_privacy=ignore_privacy,
        check_result=check_result_exists,
        raise_http_errors=raise_http_errors
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
        prefetch_tags: bool = False,
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
        prefetch_tags=prefetch_tags,
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

    tags = [{'id': tag.id, 'key': tag.key, 'value': tag.value} for tag in thing.tags.all()]
    
    return {
        'id': thing.id,
        'is_private': thing.is_private,
        'is_primary_owner': getattr(thing_association, 'is_primary_owner', False),
        'owns_thing': getattr(thing_association, 'owns_thing', False),
        'follows_thing': getattr(thing_association, 'follows_thing', False),
        'tags': tags,
        'owners': [{
            **{field: getattr(associate, field) for field in AssociationFields.__fields__.keys()},
            **{field: getattr(associate.person, field) for field in PersonFields.__fields__.keys()},
            **{field: getattr(associate.person.organization, field, None)
               for field in OrganizationFields.__fields__.keys()},
        } for associate in thing.associates.all() if associate.owns_thing is True and associate.person.is_active],
        **{field: getattr(thing, field) for field in ThingFields.__fields__.keys()},
        **{field: getattr(thing.location, field) for field in LocationFields.__fields__.keys()}
    }


def create_hydroshare_archive_resource(
        hydroshare_service,
        resource_title,
        resource_abstract,
        resource_keywords,
        thing
):

    archive_resource = hydroshare_service.create()
    archive_resource.metadata.title = resource_title
    archive_resource.metadata.abstract = resource_abstract
    archive_resource.metadata.subjects = resource_keywords
    archive_resource.metadata.spatial_coverage = PointCoverage(
        name=thing.location.name,
        north=thing.location.latitude,
        east=thing.location.longitude,
        projection='WGS 84 EPSG:4326',
        type='point',
        units='Decimal degrees'
    )
    archive_resource.metadata.additional_metadata = {
        'Sampling Feature Type': thing.sampling_feature_type,
        'Sampling Feature Code': thing.sampling_feature_code,
        'Site Type': thing.site_type
    }

    if thing.data_disclaimer:
        archive_resource.metadata.additional_metadata['Data Disclaimer'] = thing.data_disclaimer

    archive_resource.save()

    thing.hydroshare_archive_resource_id = archive_resource.resource_id
    thing.save()

    return archive_resource
