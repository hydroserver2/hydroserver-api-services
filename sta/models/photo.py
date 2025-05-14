import typing
from django.db import models
from django.conf import settings
from iam.models.utils import PermissionChecker
from .thing import Thing

if typing.TYPE_CHECKING:
    from django.contrib.auth import get_user_model

    User = get_user_model()


def photo_storage_path(instance, filename):
    return f"photos/{instance.thing.id}/{filename}"


class Photo(models.Model, PermissionChecker):
    thing = models.ForeignKey(Thing, related_name="photos", on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=255)
    photo = models.FileField(upload_to=photo_storage_path)

    def __str__(self):
        return f"{self.name} - {self.id}"

    @property
    def link(self):
        storage = self.photo.storage

        try:
            photo_link = storage.url(self.photo.name, expire=3600)
        except TypeError:
            photo_link = storage.url(self.photo.name)

        if settings.DEPLOYMENT_BACKEND == "local":
            photo_link = settings.PROXY_BASE_URL + photo_link

        return photo_link

    class Meta:
        unique_together = ("thing", "name")
