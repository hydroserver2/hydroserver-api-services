from django.db.models import DecimalField, ForeignKey
from django.db import models
import uuid

from accounts.models import CustomUser
from sensorthings.models import Thing


# class Site(models.Model):
#     # This model should only contain the data related to how a Thing will be managed
#     name = models.CharField(max_length=200)
#     latitude = DecimalField(max_digits=22, decimal_places=16, blank=True, null=True)
#     longitude = DecimalField(max_digits=22, decimal_places=16, blank=True, null=True)
#     elevation = DecimalField(max_digits=22, decimal_places=16, blank=True, null=True)
#     # registration_date = models.DateTimeField(auto_now_add=True)
#     # id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)


class ThingOwnership(models.Model):
    # id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    thing_id = ForeignKey(Thing, on_delete=models.CASCADE)
    person_id = ForeignKey(CustomUser, on_delete=models.CASCADE)
    owns_thing = models.BooleanField(default=False)
    follows_thing = models.BooleanField(default=False)
