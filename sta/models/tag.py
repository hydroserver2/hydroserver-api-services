import typing
from typing import Optional, Union
from django.db import models
from django.db.models import Q
from iam.models.utils import PermissionChecker
from .thing import Thing

if typing.TYPE_CHECKING:
    from django.contrib.auth import get_user_model
    from iam.models import APIKey

    User = get_user_model()


class TagQuerySet(models.QuerySet):
    def visible(self, principal: Optional[Union["User", "APIKey"]]):
        if hasattr(principal, "account_type"):
            if principal.account_type == "admin":
                return self
            else:
                return self.filter(
                    Q(thing__workspace__is_private=False, thing__is_private=False)
                    | Q(thing__workspace__owner=principal)
                    | Q(
                        thing__workspace__collaborators__user=principal,
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
        elif hasattr(principal, "workspace"):
            return self.filter(
                Q(thing__workspace__is_private=False, thing__is_private=False)
                | Q(
                    thing__workspace__apikeys=principal,
                    thing__workspace__apikeys__role__permissions__resource_type__in=[
                        "*",
                        "Thing",
                    ],
                    thing__workspace__apikeys__role__permissions__permission_type__in=[
                        "*",
                        "view",
                    ],
                )
            )
        else:
            return self.filter(
                Q(thing__workspace__is_private=False, thing__is_private=False)
            )


class Tag(models.Model, PermissionChecker):
    thing = models.ForeignKey(Thing, related_name="tags", on_delete=models.DO_NOTHING)
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

    objects = TagQuerySet.as_manager()
