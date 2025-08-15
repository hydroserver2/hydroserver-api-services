import uuid
from typing import Optional
from ninja.errors import HttpError
from allauth.socialaccount.models import SocialToken, SocialApp
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from etl.models import DataArchive, OrchestrationSystem
from etl.schemas import (
    HydroShareArchivalFields,
    HydroShareArchivalPostBody,
    HydroShareArchivalPatchBody,
)
from etl.tasks import archive_to_hydroshare
from sta.services.thing import ThingService
from sta.services.datastream import DatastreamService
from api.service import ServiceUtils

User = get_user_model()
thing_service = ThingService()
datastream_service = DatastreamService()


class HydroShareArchivalService(ServiceUtils):
    def get_hydroshare_thing_archive(
        self,
        principal: User,
        uid: uuid.UUID,
    ):
        thing = thing_service.get_thing_for_action(
            principal=principal, uid=uid, action="view"
        )
        orchestration_system = self.get_hydroshare_archival_system()

        return DataArchive.objects.filter(
            orchestration_system=orchestration_system,
            workspace=thing.workspace,
            settings__thingId=str(thing.id),
        ).first()

    @staticmethod
    def get_hydroshare_archival_system():
        try:
            return OrchestrationSystem.objects.get(
                name="HydroShare Archival Manager", workspace=None
            )
        except OrchestrationSystem.DoesNotExist:
            raise HttpError(400, "HydroShare archival has not been configured")

    @staticmethod
    def get_hydroshare_tokens(
        principal: User,
    ):
        hs_client_id = (
            SocialApp.objects.filter(provider="hydroshare")
            .values_list("client_id", flat=True)
            .first()
        )
        hs_access_token = (
            SocialToken.objects.filter(
                account__user=principal, account__provider="hydroshare"
            ).first()
        )

        if not hs_client_id or not hs_access_token:
            raise HttpError(400, "No HydroShare account linked to this user account")

        return hs_client_id, hs_access_token.id

    def get(self, principal: Optional[User], uid: uuid.UUID):
        thing_archive = self.get_hydroshare_thing_archive(principal=principal, uid=uid)

        if not thing_archive:
            raise HttpError(404, "Thing archive not found")

        return {
            "thing_id": str(uid),
            "link": str(thing_archive.settings["link"]),
            "path": thing_archive.settings["path"],
            "datastreamIds": thing_archive.settings["datastreamIds"],
        }

    def create(
        self,
        principal: User,
        response: HttpResponse,
        uid: uuid.UUID,
        data: HydroShareArchivalPostBody
    ):
        thing = thing_service.get_thing_for_action(
            principal=principal, uid=uid, action="edit"
        )
        thing_archive = self.get_hydroshare_thing_archive(principal=principal, uid=uid)

        if thing_archive:
            raise HttpError(400, "Thing archive already exists")

        hs_client_id, hs_access_token = self.get_hydroshare_tokens(principal=principal)

        hydroshare_archival_system = self.get_hydroshare_archival_system()
        thing_archive = DataArchive.objects.create(
            workspace=thing.workspace,
            name=f"HydroShare Archive for Thing: {thing.name}",
            orchestration_system=hydroshare_archival_system,
            settings={
                "thingId": str(thing.id),
                "link": data.link,
                "path": data.path,
                "datastreamIds": (
                    [str(datastream_id) for datastream_id in data.datastream_ids]
                    if data.datastream_ids is not None
                    else [str(datastream.id) for datastream in thing.datastreams]
                ),
            },
        )
        thing_archive.datastreams.set(data.datastream_ids)

        return self.run_task(
            task_callable=archive_to_hydroshare,
            response=response,
            hs_client_id=str(hs_client_id),
            hs_access_token_id=str(hs_access_token),
            hs_archive_id=str(thing_archive.id),
            hs_resource_metadata={
                "resource_title": data.resource_title,
                "resource_keywords": data.resource_keywords,
                "resource_abstract": data.resource_abstract,
                "public_resource": data.public_resource,
            },
        )

    def update(
        self, principal: User, response: HttpResponse, uid: uuid.UUID, data: HydroShareArchivalPatchBody
    ):
        thing = thing_service.get_thing_for_action(
            principal=principal, uid=uid, action="edit"
        )
        thing_archive = self.get_hydroshare_thing_archive(principal=principal, uid=uid)

        if not thing_archive:
            raise HttpError(404, "Thing archive not found")

        hs_client_id, hs_access_token = self.get_hydroshare_tokens(principal=principal)

        archive_data = data.dict(
            include=set(HydroShareArchivalFields.model_fields.keys()),
            exclude_unset=True,
        )

        if "path" in archive_data:
            thing_archive.settings["path"] = archive_data["path"]

        if "link" in archive_data:
            thing_archive.settings["link"] = archive_data["link"]

        if "datastream_ids" in archive_data:
            thing_archive.settings["datastreamIds"] = (
                [str(datastream_id) for datastream_id in archive_data["datastream_ids"]]
                if archive_data["datastream_ids"] is not None
                else [str(datastream.id) for datastream in thing.datastreams]
            )
            thing_archive.datastreams.set(archive_data["datastream_ids"])

        thing_archive.save()

        return self.run_task(
            task_callable=archive_to_hydroshare,
            response=response,
            hs_client_id=str(hs_client_id),
            hs_access_token_id=str(hs_access_token),
            hs_archive_id=str(thing_archive.id),
        )

    def delete(self, principal: Optional[User], uid: uuid.UUID):
        thing_service.get_thing_for_action(principal=principal, uid=uid, action="edit")
        thing_archive = self.get_hydroshare_thing_archive(principal=principal, uid=uid)

        if not thing_archive:
            raise HttpError(404, "Thing archive not found")

        thing_archive.delete()

        return "HydroShare archive configuration removed"

    def run(self, principal: User, response: HttpResponse, uid: uuid.UUID):
        thing = thing_service.get_thing_for_action(
            principal=principal, uid=uid, action="edit"
        )
        thing_archive = self.get_hydroshare_thing_archive(principal=principal, uid=thing.id)

        if not thing_archive:
            raise HttpError(404, "Thing archive not found")

        hs_client_id, hs_access_token = self.get_hydroshare_tokens(principal=principal)

        return self.run_task(
            task_callable=archive_to_hydroshare,
            response=response,
            hs_client_id=str(hs_client_id),
            hs_access_token_id=str(hs_access_token),
            hs_archive_id=str(thing_archive.id),
        )
