from django.db.models import Q, Prefetch, Count
from core.models import Thing, ThingAssociation
from .schemas import ThingFields, LocationFields, PersonFields, OrganizationFields, AssociationFields


def build_thing_response(user, thing):
    """
    The build_thing_response function takes a user and a thing queryset as arguments. It converts the queryset to a
    dictionary, including nested owner and location fields.

    :param user: Determine whether the user is following or owns the thing
    :param thing: Pass the thing queryset to the function
    :return: A thing dictionary
    """

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


def query_things(user=None, thing_ids=None):
    """
    The query_things function takes in a user and an optional list of thing_ids.
    It returns a list of things that the user has access to, which is defined as:
        - Things that are not private (is_private=False) OR
        - Things where the user is associated with it AND owns it

    :param user: Filter the results based on whether the user is associated with the thing
    :param thing_ids: Filter the query to only return things that match the ids provided
    :return: A list of thing dictionaries
    """

    if user:
        owner_filter = (Q(is_private=False) | (Q(associates__person=user) & Q(associates__owns_thing=True)))
    else:
        owner_filter = Q(is_private=False)

    thing_query = Thing.objects.annotate(associates_count=Count('associates', filter=owner_filter))

    if thing_ids:
        thing_query = thing_query.filter(
            id__in=thing_ids
        )

    associates_prefetch = Prefetch(
        'associates', queryset=ThingAssociation.objects.select_related('person', 'person__organization')
    )

    things = thing_query.select_related('location').prefetch_related(associates_prefetch).filter(
        associates_count__gt=0
    ).all()

    things = [
        build_thing_response(user, thing) for thing in things
    ]

    return things


def get_thing_association(user, thing_id):
    """
    The get_thing_association function is used to retrieve a ThingAssociation object
    from the database. It takes in two parameters: user and thing_id. The user parameter
    is an instance of the Person model, while thing_id is an integer representing a unique
    identifier for a Thing object.

    :param user: Check if the user is associated with the thing
    :param thing_id: Get the thing_association object
    :return: A ThingAssociation object, or 403/404 if the object doesn't exist or isn't owned by the user.
    """

    thing_associations = ThingAssociation.objects.select_related(
        'thing', 'thing__location'
    ).filter(thing_id=thing_id).all()

    if not thing_associations:
        return 404

    thing_association = next(iter([
        associate for associate in thing_associations if associate.person_id == user.id
    ]), None)

    if not thing_association:
        return 403

    return thing_association


def get_thing_by_id(user, thing_id):
    """
    The get_thing_by_id function returns a single Thing object, given the user and thing_id.

    :param user: Query the database for a specific user
    :param thing_id: Specify the id of the thing we want to get
    :return: The thing with the specified id
    """

    return next(iter(query_things(
        user=user,
        thing_ids=[thing_id]
    )), None)
