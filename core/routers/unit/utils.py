from django.db.models import Q
from core.models import Unit
from .schemas import UnitFields


def query_units(user=None, unit_ids=None):
    """
    The query_units function takes in a user and unit_ids, and returns a list of units.

    :param user: Filter the units by user
    :param unit_ids: Filter the query by a list of unit IDs
    :return: A list of dictionaries containing unit details
    """

    unit_query = Unit.objects.filter(Q(person=user))

    if unit_ids:
        unit_query = unit_query.filter(
            id__in=unit_ids
        )

    units = [
        {
            'id': unit.id,
            **{field: getattr(unit, field) for field in UnitFields.__fields__.keys()},
        } for unit in unit_query.all()
    ]

    return units


def get_unit_by_id(user, unit_id):
    """
    The get_unit_by_id function returns a unit object given the user and unit_id.

    :param user: Identify the user who is requesting the unit
    :param unit_id: Specify which unit we want to get
    :return: A single unit object for a given user and unit ID
    """

    return next(iter(query_units(
        user=user,
        unit_ids=[unit_id]
    )), None)
