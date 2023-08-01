from ninja import Router, Query
from django.http import HttpRequest, HttpResponse
from django.db import transaction
from typing import List


class ThingApi:
    router = Router(tags=['Things'])

    @router.get(
        '/things',
        response={
            200: List[None]
        }
    )
    def get_things(
            self,
            request: HttpRequest,
            params = Query(...)
    ):
        """"""

        return []





# @thing_router.post(
#     '/things',
#     response=generate_post_responses(ThingGetResponse),
# )
# @transaction.atomic
# def create_thing(
#         request: HttpRequest,
#         data: ThingPostBody
# ):
#     """"""
#
#     thing = Thing.objects.create(
#         name=data.name,
#         description=data.description,
#         sampling_feature_type=data.sampling_feature_type,
#         sampling_feature_code=data.sampling_feature_code,
#         site_type=data.site_type
#     )
#
#     Location.objects.create(
#         name='Location for ' + thing.name,
#         description='location',
#         encoding_type="application/geo+json",
#         latitude=data.latitude, longitude=data.longitude, elevation=data.elevation,
#         state=data.state,
#         county=data.county,
#         thing=thing
#     )
#
#     ThingAssociation.objects.create(
#         thing=thing,
#         person=request.authenticated_user,
#         owns_thing=True,
#         is_primary_owner=True
#     )
#
#     return 201, thing
