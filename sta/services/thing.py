import uuid
from typing import Optional
from ninja.errors import HttpError
from django.contrib.auth import get_user_model
from iam.services.utils import ServiceUtils
from sta.models import Thing, Location
from sta.schemas import ThingPostBody, ThingPatchBody, TagPostBody, TagDeleteBody, PhotoPostBody, PhotoDeleteBody
from sta.schemas.thing import ThingFields, LocationFields

User = get_user_model()


class ThingService(ServiceUtils):
    @staticmethod
    def list(user: Optional[User], workspace_id: Optional[uuid.UUID]):
        queryset = Thing.objects

        if workspace_id:
            queryset = queryset.filter(workspace_id=workspace_id)

        return queryset.visible(user=user).prefetch_related("tags", "photos").with_location().distinct()

    @staticmethod
    def get(user: Optional[User], uid: uuid.UUID):
        try:
            thing = Thing.objects.select_related("workspace").prefetch_related("tags", "photos").get(pk=uid)
        except Thing.DoesNotExist:
            raise HttpError(404, "Thing does not exist")

        thing_permissions = thing.get_user_permissions(user=user)

        if "view" not in thing_permissions:
            raise HttpError(404, "Thing does not exist")

        return thing

    def create(self, user: User, data: ThingPostBody):
        workspace, _ = self.get_workspace(user=user, workspace_id=data.workspace_id)

        if not Thing.can_user_create(user=user, workspace=workspace):
            raise HttpError(403, "You do not have permission to create this Thing")

        location = Location.objects.create(
            name=f'Location for {data.name}',
            description='location',
            encoding_type="application/geo+json",
            workspace=workspace,
            **data.dict(include=set(LocationFields.model_fields.keys()))
        )

        thing = Thing.objects.create(
            workspace=workspace,
            **data.dict(include=set(ThingFields.model_fields.keys()))
        )

        thing.locations.add(location)

        return thing

    @staticmethod
    def update(user: User, uid: uuid.UUID, data: ThingPatchBody):
        try:
            thing = Thing.objects.select_related("workspace").prefetch_related("tags", "photos").get(pk=uid)
            location = thing.location
        except Thing.DoesNotExist:
            raise HttpError(404, "Thing does not exist")

        thing_permissions = thing.get_user_permissions(user=user)

        if "view" not in thing_permissions:
            raise HttpError(404, "Thing does not exist")

        if "edit" not in thing_permissions:
            raise HttpError(403, "You do not have permission to edit this Thing")

        thing_data = data.dict(include=set(ThingFields.model_fields.keys()), exclude_unset=True)
        location_data = data.dict(include=set(LocationFields.model_fields.keys()), exclude_unset=True)

        if thing_data.get("name"):
            location_data["name"] = f"Location for {thing_data['name']}"

        for field, value in thing_data.items():
            setattr(thing, field, value)

        thing.save()

        for field, value in location_data.items():
            setattr(location, field, value)

        location.save()

        return thing

    @staticmethod
    def delete(user: User, uid: uuid.UUID):
        try:
            thing = Thing.objects.select_related("workspace").prefetch_related("tags", "photos").get(pk=uid)
            location = thing.location
        except Thing.DoesNotExist:
            raise HttpError(404, "Thing does not exist")

        thing_permissions = thing.get_user_permissions(user=user)

        if "view" not in thing_permissions:
            raise HttpError(404, "Thing does not exist")

        if "delete" not in thing_permissions:
            raise HttpError(403, "You do not have permission to delete this Thing")

        thing.delete()
        location.delete()

        return "Thing deleted"

    def get_tags(self, user: Optional[User], uid: uuid.UUID):
        pass

    def add_tag(self, user: User, uid: uuid.UUID, data: TagPostBody):
        pass

    def update_tag(self, user: User, uid: uuid.UUID, data: TagPostBody):
        pass

    def remove_tag(self, user: User, uid: uuid.UUID, data: TagDeleteBody):
        pass

    def get_photos(self, user: Optional[User], uid: uuid.UUID):
        pass

    def add_photo(self, user: User, uid: uuid.UUID, data: PhotoPostBody, file):
        pass

    def update_photo(self, user: User, uid: uuid.UUID, data: PhotoPostBody, file):
        pass

    def remove_photo(self, user: User, uid: uuid.UUID, data: PhotoDeleteBody):
        pass
