from django.db import models
from django.db.models import ForeignKey
from simple_history.models import HistoricalRecords
from core.models import Thing
from django.contrib.auth import get_user_model

User = get_user_model()


class ThingAssociation(models.Model):
    thing = ForeignKey(Thing, on_delete=models.CASCADE, related_name='associates', db_column='thingId')
    person = ForeignKey(User, on_delete=models.CASCADE, related_name='thing_associations', db_column='personId')
    owns_thing = models.BooleanField(default=False, db_column='ownsThing')
    is_primary_owner = models.BooleanField(default=False, db_column='isPrimaryOwner')
    history = HistoricalRecords(custom_model_name='ThingAssociationChangeLog', related_name='log')

    class Meta:
        db_table = 'ThingAssociation'
        unique_together = ('thing', 'person')
