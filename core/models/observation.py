import uuid
import pytz
from datetime import datetime
from django.db import models
from django.db.models import Q
from django.contrib.postgres.fields import ArrayField
from core.models import Datastream, FeatureOfInterest


class ObservationQuerySet(models.QuerySet):

    def apply_permissions(self, user, method):
        if not user.permissions.enabled():
            return self

        permission_filters = []

        for permission in user.permissions.get(model='Datastream', method=method):
            for resource in permission.resources:
                if resource.model == 'Datastream':
                    permission_filters.append(
                        (Q(datastream__thing__is_private=False) & Q(datastream__is_data_visible=True) &
                         Q(datastream__is_visible=True)) | Q(datastream_id__in=resource.ids)
                    )
                elif resource.model == 'Thing':
                    permission_filters.append(
                        (Q(datastream__thing__is_private=False) & Q(datastream__is_data_visible=True) &
                         Q(datastream__is_visible=True)) | Q(datastream__thing_id__in=resource.ids)
                    )
                elif resource.model == 'DataSource':
                    permission_filters.append(
                        (Q(datastream__thing__is_private=False) & Q(datastream__is_data_visible=True) &
                         Q(datastream__is_visible=True)) | Q(datastream__data_source_id__in=resource.ids)
                    )
                elif resource.model == 'DataLoader':
                    permission_filters.append(
                        (Q(datastream__thing__is_private=False) & Q(datastream__is_data_visible=True) &
                         Q(datastream__is_visible=True)) | Q(datastream__data_source__data_loader_id__in=resource.ids)
                    )

        return self.filter(*permission_filters) if permission_filters else self

    def owner_is_active(self):
        return self.filter(
            ~(Q(datastream__thing__associates__is_primary_owner=True) &
              Q(datastream__thing__associates__person__is_active=False))
        )

    def primary_owner(self, user, include_public=False):
        query = Q(datastream__thing__associates__person=user) & Q(datastream__thing__associates__is_primary_owner=True)
        query |= (Q(datastream__thing__is_private=False) &
                  Q(datastream__is_data_visible=True) &
                  Q(datastream__is_visible=True)) if include_public else Q()
        return self.filter(query)

    def owner(self, user, include_public=False):
        query = Q(datastream__thing__associates__person=user) & Q(datastream__thing__associates__owns_thing=True)
        query |= (Q(datastream__thing__is_private=False) &
                  Q(datastream__is_data_visible=True) &
                  Q(datastream__is_visible=True)) if include_public else Q()
        return self.filter(query)

    def unaffiliated(self, user):
        return self.filter(~(Q(datastream__thing__associates__person=user) &
                             Q(datastream__thing__associates__is_owner=True)))

    def follower(self, user):
        return self.filter(Q(datastream__thing__associates__person=user) &
                           Q(datastream__thing__associates__follows_thing=True))


class Observation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    datastream = models.ForeignKey(Datastream, on_delete=models.CASCADE, db_column='datastreamId')
    feature_of_interest = models.ForeignKey(FeatureOfInterest, on_delete=models.PROTECT, null=True, blank=True,
                                            db_column='featureOfInterestId')
    phenomenon_time = models.DateTimeField(db_column='phenomenonTime')
    result = models.FloatField()
    result_time = models.DateTimeField(null=True, blank=True, db_column='resultTime')
    quality_code = models.CharField(max_length=255, null=True, blank=True, db_column='qualityCode')
    result_qualifiers = ArrayField(models.UUIDField(), null=True, blank=True, db_column='resultQualifiers')

    objects = ObservationQuerySet.as_manager()

    @property
    def primary_owner(self):
        return self.datastream.thing.associates.get(is_primary_owner=True).person

    def save(self, *args, **kwargs):
        if not self.phenomenon_time:
            self.phenomenon_time = datetime.now(pytz.utc)
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'Observation'
        managed = False
