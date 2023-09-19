from django.db.models import Q
from core.models import ProcessingLevel
from .schemas import ProcessingLevelFields


def query_processing_levels(user=None, processing_level_ids=None):
    """
    The query_processing_levels function queries the ProcessingLevel table for all processing levels that are associated
    with a user.

    :param user: Filter the processing levels by user
    :param processing_level_ids: Filter the query by a list of processing level IDs
    :return: A list of dictionaries containing processing level details
    """

    processing_level_query = ProcessingLevel.objects.filter(Q(person=user))

    if processing_level_ids:
        processing_level_query = processing_level_query.filter(
            id__in=processing_level_ids
        )

    processing_levels = [
        {
            'id': processing_level.id,
            **{field: getattr(processing_level, field) for field in ProcessingLevelFields.__fields__.keys()},
        } for processing_level in processing_level_query.all()
    ]

    return processing_levels


def get_processing_level_by_id(user, processing_level_id):
    """
    The get_processing_level_by_id function returns a single processing level object.

    :param user: Determine the user's permissions
    :param processing_level_id: Specify the processing level ID
    :return: The processing level with the specified ID
    """

    return next(iter(query_processing_levels(
        user=user,
        processing_level_ids=[processing_level_id]
    )), None)
