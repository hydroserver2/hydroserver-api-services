import uuid
from typing import Optional, Literal
from ninja.errors import HttpError
from django.contrib.auth import get_user_model
from iam.services.utils import ServiceUtils
from etl.models import EtlSystem, DataSource
from etl.schemas import HydroShareArchivalPostBody, HydroShareArchivalPatchBody
from sta.services.thing import ThingService

User = get_user_model()
thing_service = ThingService()


class HydroShareArchivalService(ServiceUtils):
    @staticmethod
    def get_hydroshare_thing_archive_for_action(
        self,
        user: User,
        uid: uuid.UUID,
        action: Literal["view", "edit", "delete"],
    ):
        thing = thing_service.get_thing_for_action(user=user, uid=uid, action=action)

        return DataSource.objects.filter(
            etl_system=uuid.UUID("eb1a26e0-75c9-415d-9895-8b0be8466139"),
            workspace=thing.workspace,
            loader_configuration__thing_id=str(thing.id)
        ).first()

    def get(self, user: Optional[User], uid: uuid.UUID):
        hydroshare_thing_archive = self.get_hydroshare_thing_archive_for_action(user=user, uid=uid, action="view")

        if not hydroshare_thing_archive:
            raise HttpError(404, "Thing archive not found")

        return hydroshare_thing_archive

    def create(self, user: User, uid: uuid.UUID, data: HydroShareArchivalPostBody):
        pass

    def update(self, user: User, uid: uuid.UUID, data: HydroShareArchivalPatchBody):
        pass

    def delete(self, user: Optional[User], uid: uuid.UUID):
        pass

    def run(self, user: Optional[User], uid: uuid.UUID):
        pass
