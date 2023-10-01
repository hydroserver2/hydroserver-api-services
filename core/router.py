from ninja import Router
from typing import List
from accounts.auth.jwt import JWTAuth
from accounts.auth.basic import BasicAuth
from accounts.auth.anonymous import anonymous_auth


class DataManagementRouter(Router):
    def dm_list(self, route, response):
        return super(DataManagementRouter, self).get(
            route,
            auth=[JWTAuth(), BasicAuth(), anonymous_auth],
            response={
                200: List[response]
            },
            by_alias=True
        )

    def dm_get(self, route, response):
        return super(DataManagementRouter, self).get(
            route,
            auth=[JWTAuth(), BasicAuth(), anonymous_auth],
            response={
                200: response,
                404: str
            },
            by_alias=True
        )

    def dm_post(self, route, response):
        return super(DataManagementRouter, self).post(
            route,
            auth=[JWTAuth(), BasicAuth()],
            response={
                201: response,
                401: str
            },
            by_alias=True
        )

    def dm_patch(self, route, response):
        return super(DataManagementRouter, self).patch(
            route,
            auth=[JWTAuth(), BasicAuth()],
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
            auth=[JWTAuth(), BasicAuth()],
            response={
                204: None,
                401: str,
                403: str,
                404: str,
                409: str
            }
        )
