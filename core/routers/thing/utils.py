from ninja.errors import HttpError
from django.db.models import Prefetch
from core.models import Thing, ThingAssociation
from .schemas import ThingFields, LocationFields, PersonFields, OrganizationFields, AssociationFields


def query_things(
        thing_ids=None,
        prefetch_photos=False,
        prefetch_datastreams=False,
):
    """"""

    thing_query = Thing.objects

    if thing_ids:
        thing_query = thing_query.filter(
            id__in=thing_ids
        )

    associates_prefetch = Prefetch(
        'associates', queryset=ThingAssociation.objects.select_related('person', 'person__organization')
    )

    thing_query = thing_query.select_related('location').prefetch_related(associates_prefetch)

    if prefetch_photos:
        thing_query = thing_query.prefetch_related('photos')
    if prefetch_datastreams:
        thing_query = thing_query.prefetch_related('datastreams')

    return thing_query.all()


def query_visible_things(
        user=None,
        thing_ids=None
):
    things = query_things(thing_ids=thing_ids)

    return [
        thing for thing in things if thing.is_private is False or (user and user.id in [
            associate.person.id for associate in thing.associates.all()
            if associate.owns_thing is True
        ])
    ]


def query_thing_by_id(
        thing_id,
        user=None,
        require_ownership=False,
        require_primary_ownership=False,
        require_unaffiliated=False,
        prefetch_photos=False,
        prefetch_datastreams=False
):

    thing = next(iter(query_things(
        thing_ids=[thing_id],
        prefetch_photos=prefetch_photos,
        prefetch_datastreams=prefetch_datastreams
    )), None)

    if not thing:
        raise HttpError(404, f'Thing with ID: {thing_id} not found.')

    owners = [
        associate.person for associate in thing.associates.all()
        if associate.owns_thing is True
    ]

    if thing.is_private and (not user or user not in owners):
        raise HttpError(403, f'You do not have permission to access Thing {thing_id}')

    if require_ownership and (not user or user not in owners):
        raise HttpError(403, f'You do not have permission to perform this action on Thing {thing_id}')

    if require_unaffiliated and (not user or user in owners):
        raise HttpError(403, f'You do not have permission to perform this action on Thing {thing_id}')

    if require_primary_ownership is True:
        primary_owner = next(iter([
            associate.person for associate in thing.associates.all()
            if associate.is_primary_owner is True
        ]), None)
        if not user or primary_owner != user:
            raise HttpError(403, f'You do not have permission to perform this action on Thing {thing_id}')

    return thing


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









    # if user:
    #     owner_filter = (Q(is_private=False) | (Q(associates__person=user) & Q(associates__owns_thing=True)))
    # else:
    #     owner_filter = Q(is_private=False)
    #
    # thing_query = Thing.objects.annotate(associates_count=Count('associates', filter=owner_filter))
    #
    # if thing_ids:
    #     thing_query = thing_query.filter(
    #         id__in=thing_ids
    #     )
    #
    # associates_prefetch = Prefetch(
    #     'associates', queryset=ThingAssociation.objects.select_related('person', 'person__organization')
    # )
    #
    # thing_query = thing_query.select_related('location').prefetch_related(associates_prefetch)
    #
    # if prefetch_photos:
    #     thing_query = thing_query.prefetch_related('photos')
    # if prefetch_datastreams:
    #     thing_query = thing_query.prefetch_related('datastreams')
    #
    # things = thing_query.filter(
    #     associates_count__gt=0
    # ).all()
    #
    # return things


# def get_thing_association(user, thing_id):
#     """
#     The get_thing_association function is used to retrieve a ThingAssociation object
#     from the database. It takes in two parameters: user and thing_id. The user parameter
#     is an instance of the Person model, while thing_id is an integer representing a unique
#     identifier for a Thing object.
#
#     :param user: Check if the user is associated with the thing
#     :param thing_id: Get the thing_association object
#     :return: A ThingAssociation object, or 403/404 if the object doesn't exist or isn't owned by the user.
#     """
#
#     thing_associations = ThingAssociation.objects.select_related(
#         'thing', 'thing__location'
#     ).filter(thing_id=thing_id).all()
#
#     if not thing_associations:
#         return 404
#
#     thing_association = next(iter([
#         associate for associate in thing_associations if associate.person_id == user.id
#     ]), None)
#
#     if not thing_association:
#         return 403
#
#     return thing_association


# def get_thing_by_id(
#         user,
#         thing_id,
#         require_ownership=False,
#         require_primary_ownership=False,
#         require_unaffiliated=False,
#         prefetch_photos=False,
#         prefetch_datastreams=False
# ):
#     """"""
#
#     thing = next(iter(query_things(
#         user=user,
#         thing_ids=[thing_id],
#         prefetch_photos=prefetch_photos,
#         prefetch_datastreams=prefetch_datastreams
#     )), None)
#
#     if not thing:
#         raise HttpError(404, f'Thing with ID: {thing_id} not found.')
#
#
#
#     return next(iter(query_things(
#         user=user,
#         thing_ids=[thing_id],
#         prefetch_photos=prefetch_photos,
#         prefetch_datastreams=prefetch_datastreams
#     )), None)
