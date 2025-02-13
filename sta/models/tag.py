import typing
from django.db import models
from iam.models.utils import PermissionChecker
from .thing import Thing

if typing.TYPE_CHECKING:
    from django.contrib.auth import get_user_model

    User = get_user_model()


class Tag(models.Model, PermissionChecker):
    thing = models.ForeignKey(Thing, related_name="tags", on_delete=models.DO_NOTHING)
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
