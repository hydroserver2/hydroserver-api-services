import uuid
from ninja import Router, Path, File
from ninja.files import UploadedFile
from hydroserver.security import bearer_auth, session_auth, anonymous_auth
from hydroserver.http import HydroServerHttpRequest
from sta.schemas import PhotoGetResponse, PhotoPostBody, PhotoDeleteBody
from sta.services import ThingService

photo_router = Router(tags=["Photos"])
thing_service = ThingService()


@photo_router.get(
    "",
    auth=[session_auth, bearer_auth, anonymous_auth],
    response={
        200: list[PhotoGetResponse],
        401: str,
        403: str,
    },
    by_alias=True
)
def get_photos(request: HydroServerHttpRequest, thing_id: Path[uuid.UUID]):
    """
    Get all photos associated with a Thing.
    """

    return 200, thing_service.get_photos(
        user=request.authenticated_user,
        uid=thing_id,
    )


@photo_router.post(
    "",
    auth=[session_auth, bearer_auth],
    response={
        201: PhotoGetResponse,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True
)
def add_photo(request: HydroServerHttpRequest, thing_id: Path[uuid.UUID], data: PhotoPostBody,
              file: UploadedFile = File(...)):
    """
    Add a photo to a thing.
    """

    return 201, thing_service.add_photo(
        user=request.authenticated_user,
        uid=thing_id,
        data=data,
        file=file
    )


@photo_router.put(
    "",
    auth=[session_auth, bearer_auth],
    response={
        200: PhotoGetResponse,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True
)
def edit_photo(request: HydroServerHttpRequest, thing_id: Path[uuid.UUID], data: PhotoPostBody,
               file: UploadedFile = File(...)):
    """
    Edit a photo of a Thing.
    """

    return 200, thing_service.update_photo(
        user=request.authenticated_user,
        uid=thing_id,
        data=data,
        file=file
    )


@photo_router.delete(
    "",
    auth=[session_auth, bearer_auth],
    response={
        204: str,
        401: str,
        403: str,
        422: str,
    },
    by_alias=True
)
def remove_photo(request: HydroServerHttpRequest, thing_id: Path[uuid.UUID], data: PhotoDeleteBody):
    """
    Remove a photo from a thing.
    """

    return 204, thing_service.remove_photo(
        user=request.authenticated_user,
        uid=thing_id,
        data=data,
    )
