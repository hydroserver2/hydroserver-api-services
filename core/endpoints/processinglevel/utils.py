import uuid
import copy
from ninja.errors import HttpError
from typing import List, Optional
from uuid import UUID
from django.db.models import Q
from django.db.models.query import QuerySet
from accounts.schemas import OrganizationFields, UserFields
from core.models import Person, ProcessingLevel
from .schemas import ProcessingLevelFields


def apply_processing_level_auth_rules(
        user: Person,
        processing_level_query: QuerySet,
        require_ownership: bool = False,
        require_ownership_or_unowned: bool = False,
        check_result: bool = False
) -> (QuerySet, bool):

    result_exists = processing_level_query.exists() if check_result is True else None

    if not user and require_ownership is True:
        raise HttpError(403, 'You are not authorized to access this Processing Level.')

    if user and require_ownership is True:
        processing_level_query = processing_level_query.filter(Q(person=user))
    elif user and require_ownership_or_unowned is True:
        processing_level_query = processing_level_query.filter(Q(person=user) | Q(person=None))
    elif not user and require_ownership_or_unowned is True:
        processing_level_query = processing_level_query.filter(Q(person=None))

    return processing_level_query, result_exists


def query_processing_levels(
        user: Person,
        check_result_exists: bool = False,
        require_ownership: bool = False,
        require_ownership_or_unowned: bool = False,
        processing_level_ids: Optional[List[UUID]] = None,
        datastream_ids: Optional[List[UUID]] = None
):

    processing_level_query = ProcessingLevel.objects

    if processing_level_ids:
        processing_level_query = processing_level_query.filter(id__in=processing_level_ids)

    if datastream_ids:
        processing_level_query = processing_level_query.filter(datastreams__id__in=datastream_ids)

    processing_level_query = processing_level_query.select_related('person', 'person__organization')

    processing_level_query, result_exists = apply_processing_level_auth_rules(
        user=user,
        processing_level_query=processing_level_query,
        require_ownership=require_ownership,
        require_ownership_or_unowned=require_ownership_or_unowned,
        check_result=check_result_exists
    )

    return processing_level_query, result_exists


def check_processing_level_by_id(
        user: Person,
        processing_level_id: UUID,
        require_ownership: bool = False,
        require_ownership_or_unowned: bool = False,
        raise_http_errors: bool = False
):

    processing_level_query, processing_level_exists = query_processing_levels(
        user=user,
        processing_level_ids=[processing_level_id],
        require_ownership=require_ownership,
        require_ownership_or_unowned=require_ownership_or_unowned,
        check_result_exists=True
    )

    processing_level = processing_level_query.exists()

    if raise_http_errors and not processing_level_exists:
        raise HttpError(404, 'ProcessingLevel not found.')
    if raise_http_errors and processing_level_exists and not processing_level:
        raise HttpError(403, 'You do not have permission to perform this action on this Processing Level.')

    return processing_level


def get_processing_level_by_id(
        user: Person,
        processing_level_id: UUID,
        require_ownership: bool = False,
        require_ownership_or_unowned: bool = False,
        raise_http_errors: bool = False
):

    processing_level_query, processing_level_exists = query_processing_levels(
        user=user,
        processing_level_ids=[processing_level_id],
        require_ownership=require_ownership,
        require_ownership_or_unowned=require_ownership_or_unowned,
        check_result_exists=True
    )

    processing_level = next(iter(processing_level_query.all()), None)

    if raise_http_errors and not processing_level_exists:
        raise HttpError(404, 'Processing Level not found.')
    if raise_http_errors and processing_level_exists and not processing_level:
        raise HttpError(403, 'You do not have permission to perform this action on this Processing Level.')

    return processing_level


def build_processing_level_response(processing_level):
    return {
        'id': processing_level.id,
        'owner': {
            'organization': {
                **{field: getattr(processing_level.person.organization, field, None)
                   for field in OrganizationFields.__fields__.keys()}
            },
            **{field: getattr(processing_level.person, field) for field in UserFields.__fields__.keys()}
        },
        **{field: getattr(processing_level, field) for field in ProcessingLevelFields.__fields__.keys()},
    }


def transfer_processing_level_ownership(datastream, new_owner, old_owner):

    if datastream.processing_level.person != old_owner or datastream.processing_level.person is None:
        return

    fields_to_compare = ['code', 'definition', 'explanation']
    same_properties = ProcessingLevel.objects.filter(
        person=new_owner,
        **{f: getattr(datastream.processing_level, f) for f in fields_to_compare}
    )

    if same_properties.exists():
        datastream.processing_level = same_properties[0]
    else:
        new_property = copy.copy(datastream.processing_level)
        new_property.id = uuid.uuid4()
        new_property.person = new_owner
        new_property.save()
        datastream.processing_level = new_property

    datastream.save()
