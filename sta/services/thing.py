import uuid
from typing import Optional, Literal, get_args
from ninja.errors import HttpError
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import QuerySet, F, Q
from iam.models import APIKey
from sta.models import Thing, Location, ThingTag, ThingFileAttachment, SamplingFeatureType, SiteType, FileAttachmentType
from sta.schemas import (
    ThingSummaryResponse,
    ThingDetailResponse,
    ThingPostBody,
    ThingPatchBody,
    TagPostBody,
    TagDeleteBody,
    FileAttachmentDeleteBody,
)
from sta.schemas.thing import ThingFields, LocationFields, ThingOrderByFields
from api.service import ServiceUtils

User = get_user_model()


class ThingService(ServiceUtils):
    def get_thing_for_action(
        self,
        principal: User | APIKey,
        uid: uuid.UUID,
        action: Literal["view", "edit", "delete"],
        expand_related: Optional[bool] = None,
    ):
        try:
            thing = Thing.objects
            if expand_related:
                thing = self.select_expanded_fields(thing)
            else:
                thing = thing.prefetch_related("thing_tags", "thing_file_attachments").with_location()
            thing = thing.get(pk=uid)
        except Thing.DoesNotExist:
            raise HttpError(404, "Thing does not exist")

        thing_permissions = thing.get_principal_permissions(principal=principal)

        if "view" not in thing_permissions:
            raise HttpError(404, "Thing does not exist")

        if action not in thing_permissions:
            raise HttpError(403, f"You do not have permission to {action} this Thing")

        return thing

    @staticmethod
    def select_expanded_fields(queryset: QuerySet) -> QuerySet:
        return (
            queryset.select_related("workspace")
            .prefetch_related("thing_tags", "thing_file_attachments")
            .with_location()
        )

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

            queryset = queryset.filter(thing_tags__key=key, thing_tags__value=value)

        return queryset.distinct()

    def list(
        self,
        principal: Optional[User | APIKey],
        response: HttpResponse,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        order_by: Optional[list[str]] = None,
        filtering: Optional[dict] = None,
        expand_related: Optional[bool] = None,
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

        if expand_related:
            queryset = self.select_expanded_fields(queryset)
        else:
            queryset = queryset.prefetch_related("thing_tags", "thing_file_attachments").with_location()

        queryset = queryset.visible(principal=principal).distinct()

        queryset, count = self.apply_pagination(queryset, response, page, page_size)

        return [
            (
                ThingDetailResponse.model_validate(thing)
                if expand_related
                else ThingSummaryResponse.model_validate(thing)
            )
            for thing in queryset.all()
        ]

    def get(
        self,
        principal: Optional[User | APIKey],
        uid: uuid.UUID,
        expand_related: Optional[bool] = None,
    ):
        thing = self.get_thing_for_action(
            principal=principal, uid=uid, action="view", expand_related=expand_related
        )

        return (
            ThingDetailResponse.model_validate(thing)
            if expand_related
            else ThingSummaryResponse.model_validate(thing)
        )

    def create(
        self,
        principal: User | APIKey,
        data: ThingPostBody,
        expand_related: Optional[bool] = None,
    ):
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

        return self.get(
            principal=principal, uid=thing.id, expand_related=expand_related
        )

    def update(
        self,
        principal: User | APIKey,
        uid: uuid.UUID,
        data: ThingPatchBody,
        expand_related: Optional[bool] = None,
    ):
        thing = self.get_thing_for_action(principal=principal, uid=uid, action="edit")
        location = thing.location

        thing_data = data.dict(
            include=set(ThingFields.model_fields.keys()), exclude_unset=True
        )
        location_data = (
            data.location.dict(
                include=set(LocationFields.model_fields.keys()), exclude_unset=True
            )
            if data.location
            else {}
        )

        if thing_data.get("name"):
            location_data["name"] = f"Location for {thing_data['name']}"

        for field, value in thing_data.items():
            setattr(thing, field, value)

        thing.save()

        for field, value in location_data.items():
            setattr(location, field, value)

        location.save()

        return self.get(
            principal=principal, uid=thing.id, expand_related=expand_related
        )

    def delete(self, principal: User | APIKey, uid: uuid.UUID):
        thing = self.get_thing_for_action(
            principal=principal, uid=uid, action="delete", expand_related=True
        )
        location = thing.location

        thing.delete()
        location.delete()

        return "Thing deleted"

    def get_tags(self, principal: Optional[User | APIKey], uid: uuid.UUID):
        thing = self.get_thing_for_action(principal=principal, uid=uid, action="view")

        return thing.thing_tags.all()

    @staticmethod
    def get_tag_keys(
        principal: Optional[User | APIKey],
        workspace_id: Optional[uuid.UUID],
        thing_id: Optional[uuid.UUID],
    ):
        queryset = ThingTag.objects

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

        if ThingTag.objects.filter(thing=thing, key=data.key).exists():
            raise HttpError(400, "Tag already exists")

        return ThingTag.objects.create(thing=thing, key=data.key, value=data.value)

    def update_tag(self, principal: User | APIKey, uid: uuid.UUID, data: TagPostBody):
        thing = self.get_thing_for_action(principal=principal, uid=uid, action="edit")

        try:
            tag = ThingTag.objects.get(thing=thing, key=data.key)
        except ThingTag.DoesNotExist:
            raise HttpError(404, "Tag does not exist")

        tag.value = data.value
        tag.save()

        return tag

    def remove_tag(self, principal: User | APIKey, uid: uuid.UUID, data: TagDeleteBody):
        thing = self.get_thing_for_action(principal=principal, uid=uid, action="edit")

        queryset = ThingTag.objects.filter(thing=thing, key=data.key)

        if data.value is not None:
            queryset = queryset.filter(value=data.value)

        deleted_count, _ = queryset.delete()

        if deleted_count == 0:
            raise HttpError(404, "Tag does not exist")

        return f"{deleted_count} tag(s) deleted"

    def get_file_attachments(self, principal: Optional[User | APIKey], uid: uuid.UUID):
        thing = self.get_thing_for_action(principal=principal, uid=uid, action="view")

        return thing.file_attachments.all()

    def add_file_attachment(self, principal: User | APIKey, uid: uuid.UUID, file):
        thing = self.get_thing_for_action(principal=principal, uid=uid, action="edit")

        if ThingFileAttachment.objects.filter(thing=thing, name=file.name).exists():
            raise HttpError(400, "File attachment already exists")

        return ThingFileAttachment.objects.create(thing=thing, name=file.name, file_attachment=file)

    def remove_file_attachment(
        self, principal: User | APIKey, uid: uuid.UUID, data: FileAttachmentDeleteBody
    ):
        thing = self.get_thing_for_action(principal=principal, uid=uid, action="edit")

        try:
            file_attachment = ThingFileAttachment.objects.get(thing=thing, name=data.name)
        except ThingFileAttachment.DoesNotExist:
            raise HttpError(404, "File attachment does not exist")

        file_attachment.file_attachment.delete()
        file_attachment.delete()

        return "File attachment deleted"

    def list_site_types(
        self,
        response: HttpResponse,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        order_desc: bool = False,
    ):
        queryset = SiteType.objects.order_by(f"{'-' if order_desc else ''}name")
        queryset, count = self.apply_pagination(queryset, response, page, page_size)

        return queryset.values_list("name", flat=True)

    def list_sampling_feature_types(
        self,
        response: HttpResponse,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        order_desc: bool = False,
    ):
        queryset = SamplingFeatureType.objects.order_by(
            f"{'-' if order_desc else ''}name"
        )
        queryset, count = self.apply_pagination(queryset, response, page, page_size)

        return queryset.values_list("name", flat=True)

    def list_file_attachment_types(
        self,
        response: HttpResponse,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        order_desc: bool = False,
    ):
        queryset = FileAttachmentType.objects.order_by(
            f"{'-' if order_desc else ''}name"
        )
        queryset, count = self.apply_pagination(queryset, response, page, page_size)

        return queryset.values_list("name", flat=True)
