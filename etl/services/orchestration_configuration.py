import uuid
from ninja.errors import HttpError
from django.contrib.auth import get_user_model
from croniter import croniter
from datetime import datetime
from iam.models import Workspace
from .orchestration_system import OrchestrationSystemService

User = get_user_model()

orchestration_system_service = OrchestrationSystemService()


class OrchestrationConfigurationUtils:
    @staticmethod
    def validate_scheduling(
        crontab=None,
        interval=None,
        interval_units=None,
    ):
        if crontab and (interval or interval_units):
            raise HttpError(
                400, "Only one of crontab schedule or interval schedule can be set"
            )

        if crontab:
            try:
                croniter(crontab, datetime.now())
            except (ValueError, AttributeError):
                raise HttpError(400, "Invalid crontab schedule")

        if interval or interval_units:
            if not (interval and interval_units):
                raise HttpError(
                    400, "Both interval and interval units must be provided"
                )
            if crontab:
                raise HttpError(
                    400, "Only one of crontab schedule or interval schedule can be set"
                )

    @staticmethod
    def validate_orchestration_system(
        user: User, orchestration_system_id: uuid.UUID, workspace: Workspace
    ):
        orchestration_system = (
            orchestration_system_service.get_orchestration_system_for_action(
                user=user, uid=orchestration_system_id, action="view", raise_400=True
            )
        )

        if orchestration_system.workspace not in {workspace, None}:
            raise HttpError(
                400,
                "The given orchestration system cannot be associated with this data source",
            )

        return orchestration_system
