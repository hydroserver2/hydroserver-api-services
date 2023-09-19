from django.db.models import Q
from core.models import ObservedProperty
from .schemas import ObservedPropertyFields


def query_observed_properties(user=None, observed_property_ids=None):
    """
    The query_observed_properties function queries the ObservedProperty table for a list of observed properties.

    :param user: Filter the query to only return observed properties that belong to the user
    :param observed_property_ids: Filter the query by observed property ID.
    :return: A list of dictionaries containing observed property details.
    """

    observed_property_query = ObservedProperty.objects.filter(Q(person=user))

    if observed_property_ids:
        observed_property_query = observed_property_query.filter(
            id__in=observed_property_ids
        )

    observed_properties = [
        {
            'id': observed_property.id,
            **{field: getattr(observed_property, field) for field in ObservedPropertyFields.__fields__.keys()},
        } for observed_property in observed_property_query.all()
    ]

    return observed_properties


def get_observed_property_by_id(user, observed_property_id):
    """
    The get_observed_property_by_id function returns a single ObservedProperty object.

    :param user: Determine which user is accessing the data
    :param observed_property_id: Specify the observed property id of the observed property to be returned
    :return: The observed property with the given ID
    """

    return next(iter(query_observed_properties(
        user=user,
        observed_property_ids=[observed_property_id]
    )), None)
