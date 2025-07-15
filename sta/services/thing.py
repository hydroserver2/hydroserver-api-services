import uuid
from typing import Optional, Literal, get_args
from ninja.errors import HttpError
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import F, Q
from iam.models import APIKey
from sta.models import Thing, Location, Tag, Photo, SamplingFeatureType, SiteType
from sta.schemas import (
    ThingPostBody,
    ThingPatchBody,
    TagPostBody,
    TagDeleteBody,
    PhotoDeleteBody,
)
from sta.schemas.thing import ThingFields, LocationFields, ThingOrderByFields
from api.service import ServiceUtils

User = get_user_model()


class ThingService(ServiceUtils):
    @staticmethod
    def get_thing_for_action(
        principal: User | APIKey,
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
    def apply_bbox_filter(queryset, bbox: Optional[list[str]]):
        if not bbox:
            return queryset

        bbox_filter = Q()

        for bbox_str in bbox:
            try:
                parts = [float(x) for x in bbox_str.split(",")]
            except ValueError:
                raise ValueError("Bounding box must contain only numeric values")

            if len(parts) != 4:
                raise ValueError(
                    "Bounding box must have exactly 4 comma-separated values: min_lon,min_lat,max_lon,max_lat"
                )

            min_lon, min_lat, max_lon, max_lat = parts

            if min_lon > max_lon or min_lat > max_lat:
                raise ValueError(
                    "Invalid bounding box coordinates: min must be less than or equal to max"
                )

            bbox_filter |= Q(
                locations__longitude__gte=min_lon,
                locations__longitude__lte=max_lon,
                locations__latitude__gte=min_lat,
                locations__latitude__lte=max_lat,
            )

        return queryset.filter(bbox_filter)

    @staticmethod
    def apply_tag_filter(queryset, tags: list[str]):
        if not tags:
            return queryset

        for tag in tags:
            if ":" not in tag:
                raise ValueError(f"Invalid tag format: '{tag}'. Must be 'key:value'.")

            key, value = tag.split(":", 1)

            queryset = queryset.filter(tags__key=key, tags__value=value)

        return queryset.distinct()

    def list(
        self,
        principal: Optional[User | APIKey],
        response: HttpResponse,
        page: int = 1,
        page_size: int = 100,
        order_by: Optional[list[str]] = None,
        filtering: Optional[dict] = None,
    ):
        queryset = Thing.objects

        for field in [
            "workspace_id",
            "locations__state",
            "locations__county",
            "locations__country",
            "site_type",
            "sampling_feature_type",
            "is_private",
        ]:
            if field in filtering:
                if field == "is_private":
                    queryset = self.apply_filters(
                        queryset, f"is_private", filtering[field]
                    )
                    queryset = self.apply_filters(
                        queryset, f"workspace__is_private", filtering[field]
                    )
                else:
                    queryset = self.apply_filters(queryset, field, filtering[field])

        queryset = self.apply_bbox_filter(queryset, filtering.get("bbox"))
        queryset = self.apply_tag_filter(queryset, filtering.get("tag"))

        if order_by:
            queryset = self.apply_ordering(
                queryset,
                order_by,
                list(get_args(ThingOrderByFields)),
                {
                    "latitude": "location__latitude",
                    "longitude": "location__longitude",
                    "elevation_m": "location__elevation_m",
                    "elevationDatum": "location__elevation_datum",
                    "state": "location__state",
                    "county": "location__county",
                    "country": "location__country",
                },
            )

        queryset = (
            queryset.visible(principal=principal)
            .prefetch_related("tags", "photos")
            .with_location()
            .distinct()
        )

        queryset, count = self.apply_pagination(queryset, page, page_size)

        self.insert_pagination_headers(
            response=response, count=count, page=page, page_size=page_size
        )

        return queryset

    def get(self, principal: Optional[User | APIKey], uid: uuid.UUID):
        return self.get_thing_for_action(principal=principal, uid=uid, action="view")

    def create(self, principal: User | APIKey, data: ThingPostBody):
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
            **data.location.dict(include=set(LocationFields.model_fields.keys())),
        )

        return thing

    def update(self, principal: User | APIKey, uid: uuid.UUID, data: ThingPatchBody):
        thing = self.get_thing_for_action(principal=principal, uid=uid, action="edit")
        location = thing.location

        thing_data = data.dict(
            include=set(ThingFields.model_fields.keys()), exclude_unset=True
        )
        location_data = data.location.dict(
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

    def delete(self, principal: User | APIKey, uid: uuid.UUID):
        thing = self.get_thing_for_action(principal=principal, uid=uid, action="delete")
        location = thing.location

        thing.delete()
        location.delete()

        return "Thing deleted"

    def get_tags(self, principal: Optional[User | APIKey], uid: uuid.UUID):
        thing = self.get_thing_for_action(principal=principal, uid=uid, action="view")

        return thing.tags.all()

    @staticmethod
    def get_tag_keys(
        principal: Optional[User | APIKey],
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

    def add_tag(self, principal: User | APIKey, uid: uuid.UUID, data: TagPostBody):
        thing = self.get_thing_for_action(principal=principal, uid=uid, action="edit")

        if Tag.objects.filter(thing=thing, key=data.key).exists():
            raise HttpError(400, "Tag already exists")

        return Tag.objects.create(thing=thing, key=data.key, value=data.value)

    def update_tag(self, principal: User | APIKey, uid: uuid.UUID, data: TagPostBody):
        thing = self.get_thing_for_action(principal=principal, uid=uid, action="edit")

        try:
            tag = Tag.objects.get(thing=thing, key=data.key)
        except Tag.DoesNotExist:
            raise HttpError(404, "Tag does not exist")

        tag.value = data.value
        tag.save()

        return tag

    def remove_tag(self, principal: User | APIKey, uid: uuid.UUID, data: TagDeleteBody):
        thing = self.get_thing_for_action(principal=principal, uid=uid, action="edit")

        queryset = Tag.objects.filter(thing=thing, key=data.key)

        if data.value is not None:
            queryset = queryset.filter(value=data.value)

        deleted_count, _ = queryset.delete()

        if deleted_count == 0:
            raise HttpError(404, "Tag does not exist")

        return f"{deleted_count} tag(s) deleted"

    def get_photos(self, principal: Optional[User | APIKey], uid: uuid.UUID):
        thing = self.get_thing_for_action(principal=principal, uid=uid, action="view")

        return thing.photos.all()

    def add_photo(self, principal: User | APIKey, uid: uuid.UUID, file):
        thing = self.get_thing_for_action(principal=principal, uid=uid, action="edit")

        if Photo.objects.filter(thing=thing, name=file.name).exists():
            raise HttpError(400, "Photo already exists")

        return Photo.objects.create(thing=thing, name=file.name, photo=file)

    def remove_photo(
        self, principal: User | APIKey, uid: uuid.UUID, data: PhotoDeleteBody
    ):
        thing = self.get_thing_for_action(principal=principal, uid=uid, action="edit")

        try:
            photo = Photo.objects.get(thing=thing, name=data.name)
        except Photo.DoesNotExist:
            raise HttpError(404, "Photo does not exist")

        photo.photo.delete()
        photo.delete()

        return "Photo deleted"

    def list_site_types(
        self,
        response: HttpResponse,
        page: int = 1,
        page_size: int = 100,
        order_desc: bool = False,
    ):
        queryset = SiteType.objects.order_by(f"{'-' if order_desc else ''}name")
        queryset, count = self.apply_pagination(queryset, page, page_size)

        self.insert_pagination_headers(
            response=response, count=count, page=page, page_size=page_size
        )

        return queryset.values_list("name", flat=True)

    def list_sampling_feature_types(
        self,
        response: HttpResponse,
        page: int = 1,
        page_size: int = 100,
        order_desc: bool = False,
    ):
        queryset = SamplingFeatureType.objects.order_by(
            f"{'-' if order_desc else ''}name"
        )
        queryset, count = self.apply_pagination(queryset, page, page_size)

        self.insert_pagination_headers(
            response=response, count=count, page=page, page_size=page_size
        )

        return queryset.values_list("name", flat=True)
