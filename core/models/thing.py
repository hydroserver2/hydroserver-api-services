import uuid
from django.db import models
from django.db.models import Q, Count, Prefetch
from simple_history.models import HistoricalRecords
from core.models import Location


class ThingQuerySet(models.QuerySet):

    def active_owner(self):
        return self.filter(
            ~(Q(associates__is_primary_owner=True) & Q(associates__person__is_active=False))
        )

    def primary_owner(self, user):
        auth_filters.append(Q(associates__person=user) & Q(associates__is_primary_owner=True))
        return

    def owner(self, user):
        pass

    def unaffiliated(self, user):
        pass

    def follower(self, user):
        pass


class Thing(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField()
    sampling_feature_type = models.CharField(max_length=200, db_column='samplingFeatureType')
    sampling_feature_code = models.CharField(max_length=200, db_column='samplingFeatureCode')
    site_type = models.CharField(max_length=200, db_column='siteType')
    is_private = models.BooleanField(default=False, db_column='isPrivate')
    data_disclaimer = models.TextField(null=True, blank=True, db_column='dataDisclaimer')
    hydroshare_archive_resource_id = models.CharField(
        max_length=500, blank=True, null=True, db_column='hydroshareArchiveResourceId'
    )
    location = models.OneToOneField(Location, related_name='thing', on_delete=models.CASCADE, db_column='locationId')
    history = HistoricalRecords(custom_model_name='ThingChangeLog', related_name='log')

    objects = ThingQuerySet.as_manager()

    class Meta:
        db_table = 'Thing'
