import typing
from typing import Optional
from django.db import models
from django.db.models import Q
from iam.models.utils import PermissionChecker
from .thing import Thing

if typing.TYPE_CHECKING:
    from django.contrib.auth import get_user_model

    User = get_user_model()


class TagQuerySet(models.QuerySet):
    def visible(self, user: Optional["User"]):
        if user is None:
            return self.filter(
                Q(thing__workspace__is_private=False, thing__is_private=False)
            )
        elif user.account_type == "admin":
            return self
        else:
            return self.filter(
                Q(thing__workspace__is_private=False, thing__is_private=False)
                | Q(thing__workspace__owner=user)
                | Q(
                    thing__workspace__collaborators__user=user,
                    thing__workspace__collaborators__role__permissions__resource_type__in=[
                        "*",
                        "Thing",
                    ],
                    thing__workspace__collaborators__role__permissions__permission_type__in=[
                        "*",
                        "view",
                    ],
                )
            )


class Tag(models.Model, PermissionChecker):
    thing = models.ForeignKey(Thing, related_name="tags", on_delete=models.DO_NOTHING)
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

    objects = TagQuerySet.as_manager()
