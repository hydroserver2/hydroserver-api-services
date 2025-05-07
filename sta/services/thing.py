import uuid
from typing import Optional, Literal, Union
from ninja.errors import HttpError
from django.contrib.auth import get_user_model
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import F
from iam.models import APIKey
from iam.services.utils import ServiceUtils
from sta.models import Thing, Location, Tag, Photo
from sta.schemas import (
    ThingPostBody,
    ThingPatchBody,
    TagPostBody,
    TagDeleteBody,
    PhotoDeleteBody,
)
from sta.schemas.thing import ThingFields, LocationFields

User = get_user_model()


class ThingService(ServiceUtils):
    @staticmethod
    def get_thing_for_action(
        principal: Union[User, APIKey],
        uid: uuid.UUID,
        action: Literal["view", "edit", "delete"],
    ):
        try:
            thing = (
                Thing.objects.select_related("workspace")
                .prefetch_related("tags", "photos")
                .get(pk=uid)
            )
        except Thing.DoesNotExist:
            raise HttpError(404, "Thing does not exist")

        thing_permissions = thing.get_principal_permissions(principal=principal)

        if "view" not in thing_permissions:
            raise HttpError(404, "Thing does not exist")

        if action not in thing_permissions:
            raise HttpError(403, f"You do not have permission to {action} this Thing")

        return thing

    @staticmethod
    def list(
        principal: Optional[Union[User, APIKey]], workspace_id: Optional[uuid.UUID]
    ):
        queryset = Thing.objects

        if workspace_id:
            queryset = queryset.filter(workspace_id=workspace_id)

        return (
            queryset.visible(principal=principal)
            .prefetch_related("tags", "photos")
            .with_location()
            .distinct()
        )

    def get(self, principal: Optional[Union[User, APIKey]], uid: uuid.UUID):
        return self.get_thing_for_action(principal=principal, uid=uid, action="view")

    def create(self, principal: Union[User, APIKey], data: ThingPostBody):
        workspace, _ = self.get_workspace(
            principal=principal, workspace_id=data.workspace_id
        )

        if not Thing.can_principal_create(principal=principal, workspace=workspace):
            raise HttpError(403, "You do not have permission to create this Thing")

        thing = Thing.objects.create(
            workspace=workspace,
            **data.dict(include=set(ThingFields.model_fields.keys())),
        )

        Location.objects.create(
            name=f"Location for {data.name}",
            description="location",
            encoding_type="application/geo+json",
            thing=thing,
            **data.dict(include=set(LocationFields.model_fields.keys())),
        )

        return thing

    def update(
        self, principal: Union[User, APIKey], uid: uuid.UUID, data: ThingPatchBody
    ):
        thing = self.get_thing_for_action(principal=principal, uid=uid, action="edit")
        location = thing.location

        thing_data = data.dict(
            include=set(ThingFields.model_fields.keys()), exclude_unset=True
        )
        location_data = data.dict(
            include=set(LocationFields.model_fields.keys()), exclude_unset=True
        )

        if thing_data.get("name"):
            location_data["name"] = f"Location for {thing_data['name']}"

        for field, value in thing_data.items():
            setattr(thing, field, value)

        thing.save()

        for field, value in location_data.items():
            setattr(location, field, value)

        location.save()

        return thing

    def delete(self, principal: Union[User, APIKey], uid: uuid.UUID):
        thing = self.get_thing_for_action(principal=principal, uid=uid, action="delete")
        location = thing.location

        thing.delete()
        location.delete()

        return "Thing deleted"

    def get_tags(self, principal: Optional[Union[User, APIKey]], uid: uuid.UUID):
        thing = self.get_thing_for_action(principal=principal, uid=uid, action="view")

        return thing.tags

    @staticmethod
    def get_tag_keys(
        principal: Optional[Union[User, APIKey]],
        workspace_id: Optional[uuid.UUID],
        thing_id: Optional[uuid.UUID],
    ):
        queryset = Tag.objects

        if workspace_id:
            queryset = queryset.filter(thing__workspace_id=workspace_id)

        if thing_id:
            queryset = queryset.filter(thing_id=thing_id)

        tags = (
            queryset.visible(principal=principal)
            .values("key")
            .annotate(values=ArrayAgg(F("value"), distinct=True))
        )

        return {entry["key"]: entry["values"] for entry in tags}

    def add_tag(
        self, principal: Union[User, APIKey], uid: uuid.UUID, data: TagPostBody
    ):
        thing = self.get_thing_for_action(principal=principal, uid=uid, action="edit")

        if Tag.objects.filter(thing=thing, key=data.key).exists():
            raise HttpError(400, "Tag already exists")

        return Tag.objects.create(thing=thing, key=data.key, value=data.value)

    def update_tag(
        self, principal: Union[User, APIKey], uid: uuid.UUID, data: TagPostBody
    ):
        thing = self.get_thing_for_action(principal=principal, uid=uid, action="edit")

        try:
            tag = Tag.objects.get(thing=thing, key=data.key)
        except Tag.DoesNotExist:
            raise HttpError(404, "Tag does not exist")

        tag.value = data.value
        tag.save()

        return tag

    def remove_tag(
        self, principal: Union[User, APIKey], uid: uuid.UUID, data: TagDeleteBody
    ):
        thing = self.get_thing_for_action(principal=principal, uid=uid, action="edit")

        try:
            tag = Tag.objects.get(thing=thing, key=data.key)
        except Tag.DoesNotExist:
            raise HttpError(404, "Tag does not exist")

        tag.delete()

        return "Tag deleted"

    def get_photos(self, principal: Optional[Union[User, APIKey]], uid: uuid.UUID):
        thing = self.get_thing_for_action(principal=principal, uid=uid, action="view")

        return thing.photos

    def add_photo(self, principal: Union[User, APIKey], uid: uuid.UUID, file):
        thing = self.get_thing_for_action(principal=principal, uid=uid, action="edit")

        if Photo.objects.filter(thing=thing, name=file.name).exists():
            raise HttpError(400, "Photo already exists")

        return Photo.objects.create(thing=thing, name=file.name, photo=file)

    def remove_photo(
        self, principal: Union[User, APIKey], uid: uuid.UUID, data: PhotoDeleteBody
    ):
        thing = self.get_thing_for_action(principal=principal, uid=uid, action="edit")

        try:
            photo = Photo.objects.get(thing=thing, name=data.name)
        except Photo.DoesNotExist:
            raise HttpError(404, "Photo does not exist")

        photo.photo.delete()
        photo.delete()

        return "Photo deleted"
