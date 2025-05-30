import uuid
from ninja import Router, Path, File
from ninja.files import UploadedFile
from hydroserver.security import bearer_auth, session_auth, apikey_auth, anonymous_auth
from hydroserver.http import HydroServerHttpRequest
from sta.schemas import PhotoGetResponse, PhotoDeleteBody
from sta.services import ThingService

photo_router = Router(tags=["Photos"])
thing_service = ThingService()


@photo_router.get(
    "",
    auth=[session_auth, bearer_auth, apikey_auth, anonymous_auth],
    response={
        200: list[PhotoGetResponse],
        401: str,
        403: str,
    },
    by_alias=True,
)
def get_photos(request: HydroServerHttpRequest, thing_id: Path[uuid.UUID]):
    """
    Get all photos associated with a Thing.
    """

    return 200, thing_service.get_photos(
        principal=request.principal,
        uid=thing_id,
    )


@photo_router.post(
    "",
    auth=[session_auth, bearer_auth, apikey_auth],
    response={
        201: PhotoGetResponse,
        400: str,
        401: str,
        403: str,
        413: str,
        422: str,
    },
    by_alias=True,
)
def add_photo(
    request: HydroServerHttpRequest,
    thing_id: Path[uuid.UUID],
    file: UploadedFile = File(...),
):
    """
    Add a photo to a thing.
    """

    return 201, thing_service.add_photo(
        principal=request.principal, uid=thing_id, file=file
    )


@photo_router.delete(
    "",
    auth=[session_auth, bearer_auth, apikey_auth],
    response={
        204: str,
        400: str,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True,
)
def remove_photo(
    request: HydroServerHttpRequest, thing_id: Path[uuid.UUID], data: PhotoDeleteBody
):
    """
    Remove a photo from a thing.
    """

    return 204, thing_service.remove_photo(
        principal=request.principal,
        uid=thing_id,
        data=data,
    )
