from ninja import Router
from typing import List
from hydroserver.auth import JWTAuth, BasicAuth, APIKeyHeaderAuth, anonymous_auth


class DataManagementRouter(Router):
    def dm_list(self, route, response):
        return super(DataManagementRouter, self).api_operation(
            ['GET'],  # ['GET', 'HEAD'],
            route,
            auth=[JWTAuth(), BasicAuth(), APIKeyHeaderAuth(), anonymous_auth],
            response={
                200: List[response]
            },
            by_alias=True,
        )

    def dm_get(self, route, response):
        return super(DataManagementRouter, self).api_operation(
            ['GET'],  # ['GET', 'HEAD'],
            route,
            auth=[JWTAuth(), BasicAuth(), APIKeyHeaderAuth(), anonymous_auth],
            response={
                200: response,
                403: str,
                404: str
            },
            by_alias=True
        )

    def dm_post(self, route, response):
        return super(DataManagementRouter, self).post(
            route,
            auth=[JWTAuth(), BasicAuth(), APIKeyHeaderAuth()],
            response={
                201: response,
                401: str,
                403: str,
                404: str
            },
            by_alias=True
        )

    def dm_patch(self, route, response):
        return super(DataManagementRouter, self).patch(
            route,
            auth=[JWTAuth(), BasicAuth(), APIKeyHeaderAuth()],
            response={
                203: response,
                401: str,
                403: str,
                404: str,
            },
            by_alias=True
        )

    def dm_delete(self, route):
        return super(DataManagementRouter, self).delete(
            route,
            auth=[JWTAuth(), BasicAuth(), APIKeyHeaderAuth()],
            response={
                204: None,
                401: str,
                403: str,
                404: str,
                409: str
            }
        )
