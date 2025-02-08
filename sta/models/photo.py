import typing
from django.db import models
from django.core.files.storage import storages
from iam.models.utils import PermissionChecker

if typing.TYPE_CHECKING:
    from django.contrib.auth import get_user_model

    User = get_user_model()


class Photo(models.Model, PermissionChecker):
    thing = models.ForeignKey("Thing", related_name="photos", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    photo = models.FileField(upload_to="photos", storage=storages.backends["default"])

    @property
    def link(self):
        return "https://www.example.com/photo.jpeg"
