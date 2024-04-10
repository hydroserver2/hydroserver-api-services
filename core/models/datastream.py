import uuid
from datetime import datetime
from typing import Optional
from django.db import models
from django.db.models import Q, Prefetch
from ninja.errors import HttpError
from simple_history.models import HistoricalRecords
from core.models import Thing, Sensor, ObservedProperty, ProcessingLevel, Unit, DataSource
from core.schemas.datastream import DatastreamFields


class DatastreamQuerySet(models.QuerySet):

    def apply_permissions(self, user, method):
        if not user.permissions.enabled():
            return self

        permission_filters = []

        for permission in user.permissions.get(model='Datastream', method=method):
            for resource in permission.resources:
                if resource.model == 'Datastream':
                    permission_filters.append(
                        (Q(thing__is_private=False) & Q(is_data_visible=True))
                        | Q(id__in=resource.ids)
                    )
                elif resource.model == 'Thing':
                    permission_filters.append(
                        (Q(thing__is_private=False) & Q(is_data_visible=True))
                        | Q(thing_id__in=resource.ids)
                    )
                elif resource.model == 'DataSource':
                    permission_filters.append(
                        (Q(thing__is_private=False) & Q(is_data_visible=True))
                        | Q(data_source_id__in=resource.ids)
                    )
                elif resource.model == 'DataLoader':
                    permission_filters.append(
                        (Q(thing__is_private=False) & Q(is_data_visible=True))
                        | Q(data_source__data_loader_id__in=resource.ids)
                    )

        return self.filter(*permission_filters) if permission_filters else self

    def owner_is_active(self):
        return self.filter(
            ~(Q(thing__associates__is_primary_owner=True) & Q(thing__associates__person__is_active=False))
        )

    def primary_owner(self, user, include_public=False):
        query = Q(thing__associates__person=user) & Q(thing__associates__is_primary_owner=True)
        query |= (Q(thing__is_private=False) & Q(is_data_visible=True)) if include_public else Q()
        return self.filter(query)

    def owner(self, user, include_public=False):
        query = Q(thing__associates__person=user) & Q(thing__associates__owns_thing=True)
        query |= (Q(thing__is_private=False) & Q(is_data_visible=True)) if include_public else Q()
        return self.filter(query)

    def unaffiliated(self, user):
        return self.filter(~(Q(thing__associates__person=user) & Q(thing__associates__is_owner=True)))

    def follower(self, user):
        return self.filter(Q(thing__associates__person=user) & Q(thing__associates__follows_thing=True))

    def prefetch_associates(self):
        from core.models import ThingAssociation
        associates_prefetch = Prefetch(
            'thing__associates', queryset=ThingAssociation.objects.select_related('person', 'person__organization')
        )
        return self.prefetch_related(associates_prefetch)

    def modified_since(self, modified: Optional[datetime] = None):
        return self.prefetch_related('log').filter(
           log__history_date__gt=modified
        ) if modified is not None else self

    def get_by_id(self, datastream_id, user, method, raise_404=False):
        queryset = self.select_related('processing_level', 'unit', 'time_aggregation_interval_units')
        queryset = queryset.prefetch_associates()  # noqa
        queryset = queryset.owner_is_active()

        if method == 'GET':
            queryset = queryset.owner(user=user, include_public=True)
        elif method == 'PATCH':
            queryset = queryset.owner(user=user)
        elif method == 'DELETE':
            queryset = queryset.primary_owner(user=user)

        if user.permissions.enabled():
            queryset = queryset.apply_permissions(user=user, method=method)

        try:
            thing = queryset.distinct().get(pk=datastream_id)
        except Thing.DoesNotExist:
            if raise_404:
                raise HttpError(404, 'Datastream not found.')
            else:
                return None

        return thing


class Datastream(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    thing = models.ForeignKey(Thing, on_delete=models.CASCADE, db_column='thingId', related_name='datastreams')
    sensor = models.ForeignKey(Sensor, on_delete=models.PROTECT, db_column='sensorId', related_name='datastreams')
    observed_property = models.ForeignKey(
        ObservedProperty, on_delete=models.PROTECT, db_column='observedPropertyId', related_name='datastreams'
    )
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, db_column='unitId', related_name='datastreams')
    processing_level = models.ForeignKey(
        ProcessingLevel, on_delete=models.PROTECT, db_column='processingLevelId', related_name='datastreams'
    )
    observation_type = models.CharField(max_length=255, db_column='observationType')
    result_type = models.CharField(max_length=255, db_column='resultType')
    status = models.CharField(max_length=255, null=True, blank=True)
    sampled_medium = models.CharField(max_length=255, db_column='sampledMedium')
    value_count = models.IntegerField(null=True, blank=True, db_column='valueCount')
    no_data_value = models.FloatField(db_column='noDataValue')
    intended_time_spacing = models.FloatField(null=True, blank=True, db_column='intendedTimeSpacing')
    intended_time_spacing_units = models.CharField(
        max_length=255, null=True, blank=True, db_column='intendedTimeSpacingUnits'
    )
    aggregation_statistic = models.CharField(max_length=255, db_column='aggregationStatistic')
    time_aggregation_interval = models.FloatField(db_column='timeAggregationInterval')
    time_aggregation_interval_units = models.ForeignKey(Unit, on_delete=models.PROTECT,
                                                        related_name='time_aggregation_interval_units',
                                                        db_column='timeAggregationIntervalUnitsId')
    phenomenon_begin_time = models.DateTimeField(null=True, blank=True, db_column='phenomenonBeginTime')
    phenomenon_end_time = models.DateTimeField(null=True, blank=True, db_column='phenomenonEndTime')

    is_visible = models.BooleanField(default=True, db_column='isVisible')
    is_data_visible = models.BooleanField(default=True, db_column='isDataVisible')
    data_source = models.ForeignKey(
        DataSource, on_delete=models.SET_NULL, null=True, blank=True, db_column='dataSourceId'
    )
    data_source_column = models.CharField(max_length=255, null=True, blank=True, db_column='dataSourceColumn')

    # In the data model, not implemented for now
    observed_area = models.CharField(max_length=255, null=True, blank=True, db_column='observedArea')
    result_end_time = models.DateTimeField(null=True, blank=True, db_column='resultEndTime')
    result_begin_time = models.DateTimeField(null=True, blank=True, db_column='resultBeginTime')
    history = HistoricalRecords(custom_model_name='DatastreamChangeLog', related_name='log')

    objects = DatastreamQuerySet.as_manager()

    def serialize(self):
        return {
            'id': self.id,
            'thing_id': self.thing_id,
            **{field: getattr(self, field) for field in DatastreamFields.__fields__.keys()},
        }

    class Meta:
        db_table = 'Datastream'
